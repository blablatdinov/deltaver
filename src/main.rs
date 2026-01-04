use deltaver::cli;

fn main() {
    match cli::run() {
        Ok(()) => {

        },
        Err(err) => {
            eprintln!("Error: {}", err);
            for cause in err.chain().skip(1) {
                eprintln!(" {}", cause)
            }
            std::process::exit(1);
        }
    }
}
