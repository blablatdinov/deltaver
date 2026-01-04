use anyhow::{Context, Result};
use std::env;
use std::fs;

use crate::parsers::{Parser, RequirementsParser};

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
