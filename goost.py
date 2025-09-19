import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich import box
import time

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.6",
    "Connection": "keep-alive",
    "Host": "goo.st",
    "Referer": "https://softwaresolutionshere.com/  ",
    "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Brave";v="140"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

console = Console(style="bold red")

BANNER = r"""
 __  __   ___                                                                                                 
|  |/  `.'   `.                                                                                               
|   .-.  .-.   '.-,.--. .-,.--.     .-''` ''-.        .-''` ''-.         .|                                   
|  |  |  |  |  ||  .-. ||  .-. |  .'          '.    .'          '.     .' |_                                  
|  |  |  |  |  || |  | || |  | | /              `  /              `  .'     |       _     _    _  .--------.  
|  |  |  |  |  || |  '- | |  '- |         .-.    ||         .-.    |   |  |      .' |   | '  / | |____    |  
|  |  |  |  |  || |     | |      .        |   |   ..        |   |   .   |  |    .'.'| |///  | /  |     /   /   
|__|  |__|  |__|| |     | |      .       '._.'  /  .       '._.'  /    |  '.'.'.'.-'  /|   `'.  |   .'   /    
                | |     | |       '._         .'    '._         .'     |   / .'   \_.' '   .'|  '/|  /    /___  
                |_|     |_|         '-....-'`         '-....-'`       `'-'             `-'  `--' |_________| 
"""

def bypass_link(short_code):
    """Verilen kısa kod için bypass işlemi yapar ve yönlendirme URL'sini döndürür."""
    url = f"https://goo.st/links/statistics/{short_code}"
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=False, timeout=15)
        if response.status_code in [301, 302, 303, 307, 308] and 'location' in response.headers:
            bypassed_url = response.headers['location']
            return bypassed_url
        else:
            console.print(f"[!] Beklenen yönlendirme alınamadı: {short_code} | Status: {response.status_code}", style="red")
            return None
    except Exception as e:
        console.print(f"[!] Hata oluştu: {short_code} | {e}", style="red")
        return None
        
        
def main():
    console.print(Panel.fit(
        Text(BANNER, style="red"),
        title="[bold red]Goo.st Bypass Aracı[/bold red]",
        border_style="red",
        padding=(1, 2)
    ))

    console.print("[bold red]Geliştirici: https://github.com/mrr00tsuz[/bold red]\n", justify="center")

    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        console.print("[!] urls.txt dosyası bulunamadı!", style="red on black")
        return

    short_codes = []
    for line in lines:
        if line.startswith("https://goo.st/"):
            short_code = line.replace("https://goo.st/", "").strip()
            if short_code:
                short_codes.append(short_code)
            else:
                console.print(f"[!] Boş kısa kod: {line}", style="red")
        else:
            console.print(f"[!] Geçersiz format: {line}", style="red")

    if not short_codes:
        console.print("[!] Hiç geçerli link bulunamadı.", style="red")
        return

    console.print(f"\n[bold red]{len(short_codes)} adet link işleniyor...[/bold red]\n")

    results = []

    with Progress(
        SpinnerColumn(spinner_name="dots", style="red"),
        TextColumn("[progress.description]{task.description}", style="red"),
        BarColumn(bar_width=None, style="red", complete_style="red", finished_style="red"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%", style="red"),
        TimeRemainingColumn(),
        console=console,
        transient=False
    ) as progress:

        task = progress.add_task("[red]Linkler işleniyor...", total=len(short_codes))

        with ThreadPoolExecutor(max_workers=30) as executor:
            future_to_code = {executor.submit(bypass_link, code): code for code in short_codes}
            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    console.print(f"[!] {code} için hata: {exc}", style="red")
                progress.advance(task)

    time.sleep(0.5)

    if results:
        table = Table(title="[bold red]BAŞARIYLA BYPASS EDİLEN LİNKLER[/bold red]", box=box.SIMPLE, style="red")
        table.add_column("Sıra", justify="center", style="red", no_wrap=True)
        table.add_column("URL", style="red")

        for i, url in enumerate(results, 1):
            table.add_row(str(i), url)

        console.print("\n", table)


        with open("bypass.txt", "w", encoding="utf-8") as f:
            f.write(BANNER + "\n")
            f.write("                                     DEV - https://github.com/mrr00tsuz  \n\n")
            for url in results:
                f.write(url + "\n")

        console.print(f"\n[bold red] Toplam {len(results)} adet bypass edilmiş link 'bypass.txt' dosyasına kaydedildi.[/bold red]")
    else:
        console.print("\n[bold red] Hiçbir link başarıyla bypass edilemedi.[/bold red]")

if __name__ == "__main__":
    main()