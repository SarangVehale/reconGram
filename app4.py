import requests
import random
import time
from typing import Dict, Optional
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
import sys
import os
import re
from datetime import datetime
import uuid

class InstagramOSINT:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.base_url = "https://www.instagram.com"
        self.ajax_url = "https://www.instagram.com/api/v1"
        self.last_request_time = 0
        self.min_request_interval = 2
        self.device_id = self._generate_device_id()

    def _generate_device_id(self) -> str:
        """Generate a random device ID"""
        return str(uuid.uuid4())

    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def _get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        Implement proxy rotation logic here
        """
        return None

    def _get_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'X-IG-App-ID': '936619743392459',
            'X-IG-WWW-Claim': '0',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/'
        }

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        phone = re.sub(r'\D', '', phone)
        return len(phone) >= 10 and len(phone) <= 15

    def _rotate_session(self):
        """Create a new session with fresh cookies"""
        self.session = requests.Session()
        try:
            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/accounts/login/",
                headers=self._get_headers(),
                proxies=self._get_random_proxy()
            )
            time.sleep(1)
        except requests.RequestException:
            pass

    def check_username(self, username: str) -> Dict[str, any]:
        """Check Instagram username"""
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
            'error': None,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            self._rate_limit()
            url = f'{self.base_url}/{username}/'
            headers = self._get_headers()

            response = self.session.get(
                url,
                headers=headers,
                proxies=self._get_random_proxy(),
                timeout=10
            )

            if response.status_code == 200:
                result['exists'] = True
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    scripts = soup.find_all('script', type='application/ld+json')
                    for script in scripts:
                        try:
                            data = json.loads(script.string)
                            if 'mainEntityofPage' in data:
                                result.update({
                                    'follower_count': data.get('mainEntityofPage', {}).get('interactionStatistic', {}).get('userInteractionCount'),
                                    'full_name': data.get('name'),
                                    'biography': data.get('description'),
                                    'profile_pic_url': data.get('image')
                                })
                                break
                        except json.JSONDecodeError:
                            continue

                    result['is_private'] = 'This Account is Private' in response.text

                except Exception as e:
                    result['error'] = f"Error parsing data: {str(e)}"

            elif response.status_code == 404:
                result['exists'] = False
            else:
                result['error'] = f"Unexpected status code: {response.status_code}"

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"

        return result

    def check_email(self, email: str) -> Dict[str, any]:
        """Check if email is associated with an Instagram account"""
        if not self._validate_email(email):
            return {'error': 'Invalid email format', 'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        result = {
            'email': email,
            'exists': False,
            'username': None,
            'error': None,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            self._rotate_session()

            url = f"{self.base_url}/api/v1/users/lookup/"

            headers = self._get_headers()
            headers.update({
                'X-CSRFToken': self.session.cookies.get('csrftoken', ''),
                'X-Instagram-AJAX': '1'
            })

            data = {
                'email': email,
                'device_id': self.device_id,
                'email_flow': 'user_lookup',
                'guid': str(uuid.uuid4()),
                'waterfall_id': str(uuid.uuid4())
            }

            self._rate_limit()
            response = self.session.post(
                url,
                headers=headers,
                data=data,
                proxies=self._get_random_proxy(),
                timeout=10
            )

            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if json_response.get('status') == 'ok':
                        if json_response.get('obfuscated_email'):
                            result['exists'] = True
                            result['obfuscated_email'] = json_response.get('obfuscated_email')
                        if json_response.get('user'):
                            result['username'] = json_response['user'].get('username')
                    elif json_response.get('message'):
                        if 'email not found' in json_response['message'].lower():
                            result['exists'] = False
                        else:
                            result['error'] = json_response['message']
                except json.JSONDecodeError:
                    result['error'] = "Could not parse response"
            else:
                result['error'] = f"Request failed with status code: {response.status_code}"

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"

        return result

    def check_phone(self, phone: str) -> Dict[str, any]:
        """Check if phone number is associated with an Instagram account"""
        if not self._validate_phone(phone):
            return {'error': 'Invalid phone number format', 'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        # Clean and format the phone number
        phone = re.sub(r'\D', '', phone)  # Remove non-digits
        
        result = {
            'phone': phone,
            'exists': False,
            'username': None,
            'error': None,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            # Initialize a fresh session
            self._rotate_session()
            time.sleep(1)

            # First get the CSRF token and cookies
            init_url = f"{self.base_url}/accounts/login/"
            init_headers = self._get_headers()
            init_headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1'
            })
            
            init_response = self.session.get(
                init_url,
                headers=init_headers,
                proxies=self._get_random_proxy()
            )
            
            if init_response.status_code != 200:
                result['error'] = "Failed to initialize session"
                return result

            # Updated endpoint for phone verification
            url = f"{self.base_url}/accounts/account_recovery_send_ajax/"
            
            headers = self._get_headers()
            headers.update({
                'X-CSRFToken': self.session.cookies.get('csrftoken', ''),
                'X-Instagram-AJAX': '1',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.instagram.com',
                'Referer': 'https://www.instagram.com/accounts/password/reset/',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': '*/*'
            })

            # Format phone number
            if phone.startswith('91'):  # For Indian numbers
                formatted_phone = phone
            elif phone.startswith('1'):  # For US/Canada numbers
                formatted_phone = phone
            else:
                formatted_phone = f"91{phone}" if len(phone) == 10 else phone

            data = {
                'email_or_username': formatted_phone,
                'recaptcha_challenge_field': '',
                'flow': '',
                'app_id': '',
                'source_account_id': ''
            }

            self._rate_limit()
            response = self.session.post(
                url,
                headers=headers,
                data=data,
                proxies=self._get_random_proxy(),
                timeout=15
            )

            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if json_response.get('status') == 'ok':
                        result['exists'] = True
                    elif json_response.get('message'):
                        if 'no users found' in json_response['message'].lower():
                            result['exists'] = False
                        else:
                            result['error'] = json_response['message']
                except json.JSONDecodeError:
                    result['error'] = "Could not parse response"
            else:
                # Try alternative endpoint
                try:
                    alt_url = f"{self.base_url}/api/v1/users/lookup/"
                    alt_data = {
                        'phone_number': formatted_phone,
                        'trust_signal': '',
                        'guid': str(uuid.uuid4()),
                        'device_id': self.device_id,
                        'waterfall_id': str(uuid.uuid4())
                    }

                    self._rate_limit()
                    alt_response = self.session.post(
                        alt_url,
                        headers=headers,
                        data=alt_data,
                        proxies=self._get_random_proxy(),
                        timeout=15
                    )

                    if alt_response.status_code == 200:
                        json_response = alt_response.json()
                        if json_response.get('status') == 'ok':
                            result['exists'] = True
                            if json_response.get('user'):
                                result['username'] = json_response['user'].get('username')
                        elif 'no users found' in str(json_response.get('message', '')).lower():
                            result['exists'] = False
                    else:
                        result['error'] = f"Request failed with status code: {alt_response.status_code}"
                except Exception as e:
                    result['error'] = f"Alternative method failed: {str(e)}"

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"

        return result

    def print_results(self, result: Dict[str, any]) -> None:
        """Pretty print the results"""
        print("\n" + "="*50)

        if 'phone' in result:
            print(f"Results for phone: {result['phone']}")
        elif 'username' in result:
            print(f"Results for @{result['username']}")
        elif 'email' in result:
            print(f"Results for email: {result['email']}")

        print("="*50)

        if result.get('error'):
            print(f"\n⚠️  Error: {result['error']}")
            return

        print(f"\n✓ Account exists: {result.get('exists', 'Unknown')}")

        if result.get('exists'):
            if 'is_private' in result:
                print(f"✓ Private account: {result['is_private']}")
            if result.get('full_name'):
                print(f"✓ Full name: {result['full_name']}")
            if result.get('follower_count'):
                print(f"✓ Followers: {result['follower_count']}")
            if result.get('biography'):
                print(f"✓ Bio: {result['biography']}")
            if result.get('profile_pic_url'):
                print(f"✓ Profile picture URL: {result['profile_pic_url']}")
            if result.get('username'):
                print(f"✓ Associated username: @{result['username']}")
            if result.get('obfuscated_phone'):
                print(f"✓ Obfuscated phone: {result['obfuscated_phone']}")
            if result.get('obfuscated_email'):
                print(f"✓ Obfuscated email: {result['obfuscated_email']}")

        if 'checked_at' in result:
            print(f"\nChecked at: {result['checked_at']}")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a cool banner"""
    banner = """
    ╔══════════════════════════════════════════╗
    ║       Instagram Advanced OSINT Tool      ║
    ║    Username/Email/Phone Number Checker   ║
    ╚══════════════════════════════════════════╝

    Created for educational purposes only.
    Use responsibly and ethically.
    """
    print(banner)

def save_result(result: Dict[str, any]):
    """Save the result to a JSON file"""
    filename = 'instagram_osint_results.json'
    try:
        # Load existing results
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                results = json.load(f)
        else:
            results = []

        # Add new result
        results.append(result)

        # Save updated results
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)

        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"\nError saving results: {str(e)}")

def main():
    clear_screen()
    print_banner()

    osint = InstagramOSINT()

    while True:
        print("\nOptions:")
        print("1. Check Instagram username")
        print("2. Check email address")
        print("3. Check phone number")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            username = input("\nEnter Instagram username to check: @")

            if not username:
                print("\n⚠️  Username cannot be empty!")
                continue

            print(f"\n🔍 Checking Instagram account: @{username}")
            print("Please wait...")

            time.sleep(random.uniform(1, 3))
            result = osint.check_username(username)

        elif choice == '2':
            email = input("\nEnter email address to check: ")

            if not email:
                print("\n⚠️  Email cannot be empty!")
                continue

            print(f"\n🔍 Checking email: {email}")
            print("Please wait...")

            time.sleep(random.uniform(1, 3))
            result = osint.check_email(email)

        elif choice == '3':
            phone = input("\nEnter phone number to check (with country code): ")

            if not phone:
                print("\n⚠️  Phone number cannot be empty!")
                continue

            print(f"\n🔍 Checking phone number: {phone}")
            print("Please wait...")

            time.sleep(random.uniform(1, 3))
            result = osint.check_phone(phone)

        elif choice == '4':
            print("\nThank you for using Instagram Advanced OSINT Tool!")
            break

        else:
            print("\n⚠️  Invalid choice! Please try again.")
            continue

        osint.print_results(result)
        save_result(result)
        input("\nPress Enter to continue...")
        clear_screen()
        print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)
