use serde::Deserialize;
use std::path::PathBuf;
use crate::cli::Formats;

#[derive(Debug, Deserialize)]
pub struct PyprojectTool {
    deltaver: Option<DeltaverConfig>
}

#[derive(Debug, Deserialize, Clone)]
pub struct DeltaverConfig {
    pub path_to_file: Option<PathBuf>,
    pub file_format: Option<String>,
    pub excluded: Option<Vec<String>>,
    pub fail_on_avg: Option<u32>,
    pub fail_on_max: Option<u32>,
}

#[derive(Debug)]
pub struct Config {
    pub path_to_file: PathBuf,
    pub file_format: Formats,
    pub excluded: Vec<String>,
    pub fail_on_avg: Option<u32>,
    pub fail_on_max: Option<u32>,
}

impl Config {
    pub fn from_cli(cli: &crate::cli::Cli) -> Self {
        let pyproject_config = Self::load_pyproject_config();
        
        let file_format = cli.file_format.clone();
        let excluded = if !cli.exclude_deps.is_empty() {
            cli.exclude_deps.clone()
        } else {
            pyproject_config
                .as_ref()
                .and_then(|c| c.excluded.clone())
                .unwrap_or_default()
        };

        let fail_on_avg = cli.fail_on_average
            .or_else(|| pyproject_config.as_ref().and_then(|c| c.fail_on_avg));
        
        let fail_on_max = cli.fail_on_max
            .or_else(|| pyproject_config.as_ref().and_then(|c| c.fail_on_max));

        Config {
            path_to_file: cli.path_to_file.clone(),
            file_format,
            excluded,
            fail_on_avg,
            fail_on_max,
        }
    }

    fn load_pyproject_config() -> Option<DeltaverConfig> {
        let content = std::fs::read_to_string("pyproject.toml").ok()?;
        let pyproject: PyprojectTool = toml::from_str(&content).ok()?;
        pyproject.deltaver
    }
}