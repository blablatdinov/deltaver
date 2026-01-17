mod config;
use deltaver::cli;

fn main() {
    let cfg = config::Config::from_cli(cli::Cli::parse());
    match cli::run(cfg) {
        Ok(()) => {}
        Err(err) => {
            eprintln!("Error: {}", err);
            for cause in err.chain().skip(1) {
                eprintln!(" {}", cause)
            }
            std::process::exit(1);
        }
    }
}
