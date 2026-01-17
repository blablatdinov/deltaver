use anyhow::{Context, Result};
use std::env;
use std::fs;
use std::path::PathBuf;

use crate::parsers::{Parser, RequirementsParser};

use clap::{ValueEnum, Parser as ClapParser};

#[derive(Debug, Clone, ValueEnum)]
pub enum Formats {
    PipFreeze,
    NpmLock,
    PoetryLock,
    Golang,
    MixLock,
}

impl Default for Formats {
    fn default() -> Self {
        Self::PipFreeze
    }
}

impl std::fmt::Display for Formats {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::PipFreeze => write!(f, "pip-freeze"),
            Self::NpmLock => write!(f, "npm-lock"),
            Self::PoetryLock => write!(f, "poetry-lock"),
            Self::Golang => write!(f, "golang"),
            Self::MixLock => write!(f, "mix-lock"),
        }
    }
}

#[derive(ClapParser, Debug)]
#[command(name="deltaver", version, author, long_about=None)]
pub struct Cli {
    #[arg(
        help=vec!(
            "Path to file which specified project dependencies.\n",
            "Examples:",
            "  - requirements.txt",
            "  - ./poetry.lock",
            "  - /home/user/code/deltaver/poetry.lock",
        ).join("\n")
    )]
    pub path_to_file: PathBuf,

    #[arg(
        short='f',
        long="format",
        value_enum,
        default_value_t=Formats::default(),
        help="Dependencies file format",
    )]
    pub file_format: Formats,

    #[arg(long = "fail-on-avg")]
    pub fail_on_average: Option<u32>,

    #[arg(long = "fail-on-max")]
    pub fail_on_max: Option<u32>,

    #[arg(long = "exclude", value_delimiter = ',')]
    pub exclude_deps: Vec<String>,

}

pub fn run() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Использование: deltaver <файл>");
        println!("Пример: deltaver requirements.txt");
        return Ok(());
    }
    let filename = &args[1];
    let content = fs::read_to_string(filename)
        .with_context(|| format!("File content not available: {}", filename))?;
    let parser = RequirementsParser;
    let packages = parser.parse(&content)?;
    println!("Packages found: {}", packages.len());
    for package in packages {
        println!("  - {}", package)
    }
    Ok(())
}
