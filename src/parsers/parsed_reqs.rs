use crate::cli::Formats;
use crate::parsers::basic;
use crate::core::Package;
use anyhow::{Context, Result};
use chrono::{DateTime, NaiveDateTime};
use serde::{Deserialize, Serialize};
use crate::parsers::parser::Parser;
use std::time::Duration;

#[derive(Debug, Default)]
pub struct ParsedReqs {
    file_content: String,
}

impl ParsedReqs {
    pub fn new(file_content: impl Into<String>) -> Self {
        ParsedReqs {
            file_content: file_content.into(),
        }
    }
}

impl Parser for ParsedReqs {
    fn reqs(&self) -> Result<Vec<Package>> {
        let mut deps = Vec::new();
        for line in self.file_content.lines() {
            if let Some((name, version)) = basic::parse_dependency_line(line) {
                deps.push((name, version));
            }
        }
        let rt = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()?;
        rt.block_on(async move {
            let client = reqwest::Client::builder()
                .timeout(Duration::from_secs(30))
                .connect_timeout(Duration::from_secs(10))
                .build()?;
            let mut tasks = tokio::task::JoinSet::new();
            for (name, version) in deps {
                let client = client.clone();
                tasks.spawn(async move {
                    let release_date = package_release_date(&client, &name, &version).await?;
                    Ok::<Package, anyhow::Error>(Package::new(name, version, release_date))
                });
            }
            let mut packages = Vec::new();
            while let Some(result) = tasks.join_next().await {
                packages.push(result??);
            }
            Ok(packages)
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct PypiRelease {
    upload_time: String,
}


#[derive(Debug, Serialize, Deserialize)]
struct PypiResponse {
    releases: std::collections::HashMap<String, Vec<PypiRelease>>
}

async fn package_release_date(
    client: &reqwest::Client,
    name: &str,
    version: &str,
) -> Result<chrono::NaiveDate, anyhow::Error> {
    let mut last_err: Option<anyhow::Error> = None;
    for attempt in 1..=3 {
        let response = client
            .get(format!("https://pypi.org/pypi/{}/json", name))
            .send()
            .await
            .and_then(|resp| resp.error_for_status())?;
        let package = response.json::<PypiResponse>().await;
        let package = match package {
            Ok(pkg) => pkg,
            Err(err) => {
                let retryable = err.is_timeout() || err.is_connect() || err.is_request() || err.is_decode();
                let err = anyhow::Error::new(err).context("Failed to decode PyPI response");
                if retryable && attempt < 3 {
                    last_err = Some(err);
                    tokio::time::sleep(Duration::from_millis(200 * attempt)).await;
                    continue;
                }
                return Err(err);
            }
        };
        for (key, value) in &package.releases {
            if version == key.as_str() {
                let last_package = value.iter().max_by(|a, b| {
                    a.upload_time.cmp(&b.upload_time)
                });
                let latest_release = match last_package  {
                    Some(r) => r.upload_time.clone(),
                    None => anyhow::bail!("Err") // TODO: describe error
                };
                if let Ok(parsed) = DateTime::parse_from_rfc3339(&latest_release) {
                    return Ok(parsed.date_naive());
                }
                let parsed = NaiveDateTime::parse_from_str(&latest_release, "%Y-%m-%dT%H:%M:%S")
                    .with_context(|| format!("Invalid release date: {}", latest_release))?;
                return Ok(parsed.date())
            }
        }
        anyhow::bail!(String::from("Release date not found"))
    }
    Err(last_err.unwrap_or_else(|| anyhow::anyhow!("PyPI request failed")))
}

pub fn create_parser(format: Formats, file_content: &str) -> Option<Box<dyn Parser>> {
    match format {
        Formats::PipFreeze => Some(Box::new(ParsedReqs::new(file_content))),
        _ => Some(Box::new(ParsedReqs::new(file_content))),
    }
}
