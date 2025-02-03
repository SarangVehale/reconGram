import requests
import random
import time
from typing import Dict, Optional
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
import os

class InstagramOSINT:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        You can implement your own proxy rotation logic here
        """
        return None

    def _get_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def check_username(self, username: str) -> Dict[str, any]:
        """
        Check Instagram username using multiple methods
        """
        result = {
            'username': username,
            'exists': False,
            'is_private': None,
            'follower_count': None,
            'following_count': None,
            'post_count': None,
            'full_name': None,
            'biography': None,
            'profile_pic_url': None,
            'error': None
        }

        try:
            url = f'https://www.instagram.com/{username}/'
            
            # Get random proxy
            proxy = self._get_random_proxy()
            
            # Make request with custom headers and proxy
            response = self.session.get(
                url,
                headers=self._get_headers(),
                proxies=proxy,
                timeout=10
            )

            # If account exists
            if response.status_code == 200:
                result['exists'] = True
                
                # Try to extract additional information
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for JSON data in script tags
                    scripts = soup.find_all('script', type='application/ld+json')
                    for script in scripts:
                        try:
                            data = json.loads(script.string)
                            if 'mainEntityofPage' in data:
                                result['follower_count'] = data.get('mainEntityofPage', {}).get('interactionStatistic', {}).get('userInteractionCount')
                                result['full_name'] = data.get('name')
                                break
                        except json.JSONDecodeError:
                            continue

                    # Check if account is private
                    result['is_private'] = 'This Account is Private' in response.text

                except Exception as e:
                    result['error'] = f"Error parsing data: {str(e)}"

            # If account doesn't exist
            elif response.status_code == 404:
                result['exists'] = False
                
            # Handle other status codes
            else:
                result['error'] = f"Unexpected status code: {response.status_code}"

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"
        
        return result

    def print_results(self, result: Dict[str, any]) -> None:
        """Pretty print the results"""
        print("\n" + "="*50)
        print(f"Results for @{result['username']}")
        print("="*50)
        
        if result['error']:
            print(f"\n⚠️  Error: {result['error']}")
            return

        print(f"\n✓ Account exists: {result['exists']}")
        
        if result['exists']:
            print(f"✓ Private account: {result['is_private']}")
            if result['full_name']:
                print(f"✓ Full name: {result['full_name']}")
            if result['follower_count']:
                print(f"✓ Followers: {result['follower_count']}")
            if result['biography']:
                print(f"✓ Bio: {result['biography']}")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a cool banner"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║         Instagram OSINT Tool             ║
    ║      Account Existence Checker           ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)

def main():
    clear_screen()
    print_banner()
    
    osint = InstagramOSINT()
    
    while True:
        print("\nOptions:")
        print("1. Check Instagram username")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == '1':
            username = input("\nEnter Instagram username to check: @")
            
            if not username:
                print("\n⚠️  Username cannot be empty!")
                continue
                
            print(f"\n🔍 Checking Instagram account: @{username}")
            print("Please wait...")
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(1, 3))
            
            result = osint.check_username(username)
            osint.print_results(result)
            
            input("\nPress Enter to continue...")
            clear_screen()
            print_banner()
            
        elif choice == '2':
            print("\nThank you for using Instagram OSINT Tool!")
            break
            
        else:
            print("\n⚠️  Invalid choice! Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
