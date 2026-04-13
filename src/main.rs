use spider::{
    configuration::{SpiderCloudConfig, SpiderCloudMode, SpiderCloudReturnFormat},
    website::Website,
};

const VERSION: &str = env!("CARGO_PKG_VERSION");

fn main() {
    dotenvy::dotenv().ok();
    let url = std::env::var("SPIDER_URL")
        .ok()
        .or_else(|| std::env::args().nth(1))
        .expect("Usage: SPIDER_URL must be set or pass URL as argument");

    let api_key = std::env::var("SPIDER_API_KEY")
        .expect("SPIDER_API_KEY must be set. Get one free at https://spider.cloud");

    println!("Spider Demo v{}\n", VERSION);
    println!("Crawling: {}\n", url);

    // Run the async crawler
    let runtime = tokio::runtime::Runtime::new().expect("Failed to create Tokio runtime");
    runtime.block_on(crawl(url, api_key));
}

async fn crawl(url: String, api_key: String) {
    let config = SpiderCloudConfig::new(&api_key)
        .with_mode(SpiderCloudMode::Smart)
        .with_return_format(SpiderCloudReturnFormat::Markdown);

    let mut website = Website::new(&url)
        .with_limit(10)
        .with_spider_cloud_config(config)
        .build()
        .expect("Failed to build website");

    let mut rx = website.subscribe(16);

    tokio::spawn(async move {
        while let Ok(page) = rx.recv().await {
            let page_url = page.get_url();
            let markdown = page.get_content();
            let status = page.status_code;

            println!("[{status}] {page_url}\n---\n{markdown}\n");
        }
    });

    website.crawl().await;
    website.unsubscribe();
}
