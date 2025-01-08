def scrape_url(url: str, output_file: str = "scraped_data.txt"):
    """
    Scrapes a website at the given URL using BeautifulSoup and writes content to a file.

    Args:
        url (str): The URL to be scraped.
        output_file (str): The path of the output file to store content.
    """
    from bs4 import BeautifulSoup
    from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader
    
    loader = RecursiveUrlLoader(
        url=url,
        extractor=lambda html: BeautifulSoup(html, "html.parser").get_text()
    )
    docs = loader.load()
    with open(output_file, "w", encoding="utf-8") as file:
        for doc in docs:
            title = doc.metadata.get("title")
            source = doc.metadata.get("source")
            content = doc.page_content
            if isinstance(title, str) and isinstance(source, str) and isinstance(content, str):
                file.write("Page Title: " + title + "\n")
                file.write("Page URL: " + source + "\n")
                file.write("Page Content:\n" + content + "\n\n")
            else:
                print("Skipped a document due to non-string content.")
    print("Data has been successfully written to", output_file)
