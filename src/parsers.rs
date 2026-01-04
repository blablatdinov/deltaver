pub mod basic;

use crate::core::Package;
use anyhow::Result;

pub trait Parser {
    fn parse(&self, content: &str) -> Result<Vec<Package>>;
}

#[derive(Debug, Default)]
pub struct RequirementsParser;

impl Parser for RequirementsParser {
    fn parse(&self, content: &str) -> Result<Vec<Package>> {
        let mut packages = Vec::new();
        for line in content.lines() {
            if let Some((name, version)) = basic::parse_dependency_line(line) {
                let package = Package::new(
                    name,
                    version,
                    chrono::NaiveDate::from_ymd_opt(2023, 1, 1).unwrap(),
                );
                packages.push(package)
            }
        }
        Ok(packages)
    }
}

pub fn create_parser(format: &str) -> Option<Box<dyn Parser>> {
    match format {
        "requirements" => Some(Box::new(RequirementsParser)),
        _ => None,
    }
}
