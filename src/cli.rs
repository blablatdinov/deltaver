use anyhow::{Context, Result, bail};
use std::env;
use std::fs;
use std::path::PathBuf;

use crate::config::Config;
use crate::parsers::parsed_reqs::create_parser;

use clap::{Parser as ClapParser, ValueEnum};

#[derive(Debug, Clone, ValueEnum, Default)]
pub enum Formats {
    #[default]
    PipFreeze,
    NpmLock,
    PoetryLock,
    Golang,
    MixLock,
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

pub fn run(cfg: Config) -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Использование: deltaver <файл>");
        println!("Пример: deltaver requirements.txt");
        return Ok(());
    }
    let filename = &args[1];
    let content = fs::read_to_string(filename)
        .with_context(|| format!("File content not available: {}", filename))?;
    let parser = match create_parser(cfg.file_format, &content) {
        Some(p) => p,
        None => {
            bail!("Error on read file content");
        }
    };
    let packages = parser.reqs()?;
    println!("Packages found: {}", packages.len());
    for package in packages {
        println!("  - {}", package)
    }
    Ok(())
}
