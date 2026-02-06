import requests
import csv
from pathlib import Path


class DataCollector:
    def __init__(self, base_url, parse_html=True):
        self.base_url = base_url
        self.parse_html = parse_html

    def fetch_data(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            # If configured to parse HTML, return a BeautifulSoup object when possible
            if self.parse_html:
                try:
                    from bs4 import BeautifulSoup

                    return BeautifulSoup(response.content, "html.parser")
                except Exception:
                    # bs4 not available or parsing failed — return raw text
                    print("Warning: failed to parse HTML content")
                    return response.text

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    return response.json()
                except ValueError:
                    print("Warning: response not valid JSON, returning raw text")
                    return response.text
            # fallback for non-JSON responses (HTML, plain text, etc.)
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def parser(self, soup, csv_path: str = "stratagems.csv"):
        if soup is None:
            return {}

        # If a raw string was returned, parse it into a BeautifulSoup object
        if isinstance(soup, str):
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(soup, "html.parser")
            except Exception:
                print("Warning: unable to parse HTML string")
                return {}

        # target all wikitables by class and merge them
        tables = soup.select(".wikitable")
        if not tables:
            print("No matching table found")
            return {}

        def parse_table(table):
            rows = []
            pending = {}  # col_index -> [value, remaining_rows]
            for row in table.find_all("tr"):
                if not getattr(row, "name", None):
                    continue

                cells = row.find_all(["th", "td"])
                if not cells:
                    continue

                out = []
                col = 0

                def consume_pending_at(col_index):
                    if col_index in pending:
                        val, rem = pending[col_index]
                        out.append(val)
                        if rem - 1 <= 0:
                            del pending[col_index]
                        else:
                            pending[col_index][1] = rem - 1
                        return True
                    return False

                for cell in cells:
                    while consume_pending_at(col):
                        col += 1

                    imgs = cell.select("span.Stratagemcodeicon img")
                    if not imgs:
                        imgs = cell.select("p img")
                    if not imgs:
                        imgs = cell.select("img")

                    if imgs:
                        alts = [
                            img.get("alt", "").strip()
                            for img in imgs
                            if img.has_attr("alt")
                        ]
                        cell_text = (
                            " | ".join(alts) if alts else cell.get_text(" ", strip=True)
                        )
                    else:
                        cell_text = cell.get_text(" ", strip=True)

                    colspan = int(cell.get("colspan", 1))
                    rowspan = int(cell.get("rowspan", 1))

                    for i in range(colspan):
                        out.append(cell_text)
                        if rowspan > 1:
                            pending[col + i] = [cell_text, rowspan - 1]
                    col += colspan

                while consume_pending_at(col):
                    col += 1

                rows.append(out)

            return rows

        # Map table indices to output filenames
        table_filenames = {
            0: csv_path,  # First table uses the provided csv_path
            1: "mission_stratagems.csv",  # Second table goes here
        }
        
        all_rows = {}
        for idx, table in enumerate(tables):
            rows = parse_table(table)
            if not rows:
                continue

            # Determine output filename for this table
            output_filename = table_filenames.get(idx, f"table_{idx}.csv")

            if not rows:
                print(f"No rows extracted from table {idx}")
                continue

            # normalize rows to equal length and write CSV
            max_cols = max(len(r) for r in rows)
            csv_file = Path(output_filename)
            with csv_file.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                for r in rows:
                    if len(r) < max_cols:
                        r = r + [""] * (max_cols - len(r))
                    writer.writerow(r)            
            
            all_rows[idx] = len(rows)
            print(f"Wrote {len(rows)} rows to {csv_file}")

        return all_rows

    def get_stratagems(self):
        Collector = DataCollector("https://helldivers.wiki.gg/wiki/Stratagems", parse_html=True)
        soup = Collector.fetch_data()
        all_rows = Collector.parser(soup)
        return all_rows

        
if __name__ == "__main__":
    Collector = DataCollector("https://helldivers.wiki.gg/wiki/Stratagems", parse_html=True)
    soup = Collector.fetch_data()
    Collector.parser(soup)
# print(f"{str(soup)[:30000]}")
