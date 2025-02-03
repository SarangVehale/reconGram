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
from colorama import init, Fore, Back, Style
import logging

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='instagram_osint.log'
)

class InstagramOSINT:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.base_url = "https://www.instagram.com"
        self.ajax_url = "https://www.instagram.com/api/v1"
        self.last_request_time = 0
        self.min_request_interval = 2
        self.device_id = self._generate_device_id()
        self.csrf_token = None
        
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

    def _rotate_session(self):
        """Create a new session with fresh cookies and tokens"""
        try:
            # Create new session
            self.session = requests.Session()
            
            # Add some delay before making request
            self._rate_limit()
            
            # Get initial cookies from main page
            init_url = f"{self.base_url}/accounts/login/"
            init_headers = self._get_headers()
            init_headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1'
            })
            
            response = self.session.get(
                init_url,
                headers=init_headers,
                proxies=self._get_random_proxy(),
                timeout=10
            )
            
            # Extract CSRF token
            if 'csrftoken' in self.session.cookies:
                self.csrf_token = self.session.cookies['csrftoken']
            
            # Add small delay after getting cookies
            time.sleep(1)
            
            return response.status_code == 200
            
        except requests.RequestException as e:
            logging.error(f"Session rotation error: {str(e)}")
            # If there's an error, create a new clean session anyway
            self.session = requests.Session()
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-IG-App-ID': '936619743392459',
            'X-ASBD-ID': '198387',
            'X-IG-WWW-Claim': '0',
            'X-Requested-With': 'XMLHttpRequest',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/'
        }
        
        if self.csrf_token:
            headers['X-CSRFToken'] = self.csrf_token
            
        return headers

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        phone = re.sub(r'\D', '', phone)
        return len(phone) >= 10 and len(phone) <= 15

    def _get_account_details(self, username: str) -> Dict[str, any]:
        """Fetch detailed account information"""
        try:
            # First try the user info endpoint
            url = f"{self.base_url}/api/v1/users/web_profile_info/?username={username}"
            headers = self._get_headers()
            headers.update({
                'X-IG-App-ID': '936619743392459',
                'X-ASBD-ID': '198387',
                'X-IG-WWW-Claim': '0'
            })
            
            self._rate_limit()
            response = self.session.get(
                url,
                headers=headers,
                proxies=self._get_random_proxy(),
                timeout=10
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    user_data = data.get('data', {}).get('user', {})
                    if user_data:
                        return {
                            'username': username,
                            'full_name': user_data.get('full_name'),
                            'biography': user_data.get('biography'),
                            'follower_count': user_data.get('edge_followed_by', {}).get('count'),
                            'following_count': user_data.get('edge_follow', {}).get('count'),
                            'post_count': user_data.get('edge_owner_to_timeline_media', {}).get('count'),
                            'is_private': user_data.get('is_private', True),  # Default to True if not found
                            'is_verified': user_data.get('is_verified'),
                            'profile_pic_url': user_data.get('profile_pic_url_hd'),
                            'external_url': user_data.get('external_url')
                        }
                except json.JSONDecodeError:
                    logging.error(f"JSON decode error for username {username}")

            # Fallback to alternative endpoint
            alt_url = f"{self.base_url}/{username}/?__a=1&__d=dis"
            response = self.session.get(
                alt_url,
                headers=self._get_headers(),
                proxies=self._get_random_proxy(),
                timeout=10
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    user_data = data.get('graphql', {}).get('user', {})
                    if user_data:
                        return {
                            'username': username,
                            'full_name': user_data.get('full_name'),
                            'biography': user_data.get('biography'),
                            'follower_count': user_data.get('edge_followed_by', {}).get('count'),
                            'following_count': user_data.get('edge_follow', {}).get('count'),
                            'post_count': user_data.get('edge_owner_to_timeline_media', {}).get('count'),
                            'is_private': user_data.get('is_private', True),  # Default to True if not found
                            'is_verified': user_data.get('is_verified'),
                            'profile_pic_url': user_data.get('profile_pic_url_hd'),
                            'external_url': user_data.get('external_url')
                        }
                except json.JSONDecodeError:
                    pass
            return {}
        except Exception as e:
            logging.error(f"Error getting account details: {str(e)}")
            return {}

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
                # Get detailed account information
                details = self._get_account_details(username)
                if details:
                    result.update(details)
                else:
                    # Fallback to basic scraping
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
                        logging.error(f"Error parsing username data: {str(e)}")

            elif response.status_code == 404:
                result['exists'] = False
            else:
                result['error'] = f"Unexpected status code: {response.status_code}"
                logging.error(f"Unexpected status code for username {username}: {response.status_code}")

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"
            logging.error(f"Request error for username {username}: {str(e)}")
        
        return result

    def check_email(self, email: str) -> Dict[str, any]:
        """Check if email is associated with an Instagram account"""
        if not self._validate_email(email):
            return {'error': 'Invalid email format', 'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        result = {
            'email': email,
            'exists': False,
            'username': None,
            'account_details': None,
            'error': None,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            # Initialize fresh session with proper cookies
            self._rotate_session()
            time.sleep(1)

            # First try the account recovery endpoint
            recovery_url = f"{self.base_url}/accounts/account_recovery_send_ajax/"
            headers = self._get_headers()
            headers.update({
                'X-Instagram-AJAX': '1',
                'X-IG-App-ID': '936619743392459',
                'X-ASBD-ID': '198387',
                'X-IG-WWW-Claim': '0',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.instagram.com',
                'Referer': 'https://www.instagram.com/accounts/password/reset/',
                'Content-Type': 'application/x-www-form-urlencoded'
            })

            recovery_data = {
                'email_or_username': email,
                'recaptcha_challenge_field': '',
                'flow': 'user_lookup',
                'app_id': '',
                'source_account_id': ''
            }

            self._rate_limit()
            recovery_response = self.session.post(
                recovery_url,
                headers=headers,
                data=recovery_data,
                proxies=self._get_random_proxy(),
                timeout=10
            )

            if recovery_response.status_code == 200:
                try:
                    json_response = recovery_response.json()
                    if json_response.get('status') == 'ok' or 'sent' in str(json_response).lower():
                        result['exists'] = True
                        # Try to extract username from response
                        if 'message' in json_response:
                            username_match = re.search(r'@([\w._]+)', json_response['message'])
                            if username_match:
                                result['username'] = username_match.group(1)
                except json.JSONDecodeError:
                    pass

            # If no username found, try the lookup endpoint
            if not result.get('username'):
                lookup_url = f"{self.base_url}/api/v1/users/lookup/"
                lookup_data = {
                    'email': email,
                    'device_id': self.device_id,
                    'email_flow': 'user_lookup',
                    'guid': str(uuid.uuid4()),
                    'waterfall_id': str(uuid.uuid4())
                }

                # Get fresh session and cookies
                self._rotate_session()
                headers = self._get_headers()
                headers.update({
                    'X-Instagram-AJAX': '1',
                    'X-IG-App-ID': '936619743392459',
                    'X-ASBD-ID': '198387',
                    'X-IG-WWW-Claim': '0'
                })

                self._rate_limit()
                lookup_response = self.session.post(
                    lookup_url,
                    headers=headers,
                    data=lookup_data,
                    proxies=self._get_random_proxy(),
                    timeout=10
                )

                if lookup_response.status_code == 200:
                    try:
                        json_response = lookup_response.json()
                        if json_response.get('status') == 'ok':
                            result['exists'] = True
                            if json_response.get('user'):
                                result['username'] = json_response['user'].get('username')
                    except json.JSONDecodeError:
                        pass

            # If we found a username, get the account details
            if result.get('username'):
                account_details = self._get_account_details(result['username'])
                if account_details:
                    result['account_details'] = account_details
            
            # If still no username but account exists, try one final lookup
            elif result['exists'] and not result['username']:
                try:
                    final_url = f"{self.base_url}/api/v1/users/check_email/"
                    final_data = {
                        'email': email,
                        'device_id': self.device_id,
                        'guid': str(uuid.uuid4())
                    }

                    self._rate_limit()
                    final_response = self.session.post(
                        final_url,
                        headers=headers,
                        data=final_data,
                        proxies=self._get_random_proxy(),
                        timeout=10
                    )

                    if final_response.status_code == 200:
                        json_response = final_response.json()
                        if json_response.get('user'):
                            result['username'] = json_response['user'].get('username')
                            if result['username']:
                                result['account_details'] = self._get_account_details(result['username'])
                except Exception as e:
                    logging.error(f"Final lookup error for email {email}: {str(e)}")

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"
            logging.error(f"Request error for email {email}: {str(e)}")

        return result

    def check_phone(self, phone: str) -> Dict[str, any]:
        """Check if phone number is associated with an Instagram account"""
        if not self._validate_phone(phone):
            return {'error': 'Invalid phone number format', 'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        # Clean and format the phone number
        phone = re.sub(r'\D', '', phone)
        
        result = {
            'phone': phone,
            'exists': False,
            'username': None,
            'account_details': None,
            'error': None,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        try:
            # Initialize session with proper cookies
            self._rotate_session()
            time.sleep(1)

            # Format phone number variations
            phone_variations = [
                phone,
                f"+{phone}",
                f"+1{phone}" if not phone.startswith('1') else phone,
                f"+91{phone}" if not phone.startswith('91') else phone
            ]

            # Try multiple endpoints with different phone formats
            endpoints = [
                {
                    'url': f"{self.base_url}/api/v1/users/lookup_phone/",
                    'data': lambda p: {
                        'phone_number': p,
                        'device_id': self.device_id,
                        'guid': str(uuid.uuid4()),
                        'waterfall_id': str(uuid.uuid4())
                    }
                },
                {
                    'url': f"{self.base_url}/api/v1/accounts/send_recovery_flow_token/",
                    'data': lambda p: {
                        'phone_number': p,
                        'device_id': self.device_id,
                        'guid': str(uuid.uuid4()),
                    }
                },
                {
                    'url': f"{self.base_url}/api/v1/users/check_phone_number/",
                    'data': lambda p: {
                        'phone_number': p,
                        'device_id': self.device_id,
                        'guid': str(uuid.uuid4())
                    }
                }
            ]

            headers = self._get_headers()
            headers.update({
                'X-Instagram-AJAX': '1',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.instagram.com',
                'Referer': 'https://www.instagram.com/accounts/password/reset/',
                'Content-Type': 'application/x-www-form-urlencoded'
            })

            for phone_variant in phone_variations:
                for endpoint in endpoints:
                    try:
                        self._rate_limit()
                        response = self.session.post(
                            endpoint['url'],
                            headers=headers,
                            data=endpoint['data'](phone_variant),
                            proxies=self._get_random_proxy(),
                            timeout=15
                        )

                        if response.status_code == 200:
                            try:
                                json_response = response.json()
                                
                                # Check for user data in response
                                if 'user' in json_response:
                                    user_data = json_response['user']
                                    result['exists'] = True
                                    result['username'] = user_data.get('username')
                                    if result['username']:
                                        result['account_details'] = self._get_account_details(result['username'])
                                    break

                                # Check for account existence indicators
                                if any(keyword in str(json_response).lower() for keyword in ['sent', 'ok', 'found', 'success']):
                                    result['exists'] = True
                                    
                                    # Try to extract username from response
                                    username = self._extract_username_from_response(json_response)
                                    if username:
                                        result['username'] = username
                                        result['account_details'] = self._get_account_details(username)
                                    break

                                # Check error messages for username information
                                if 'message' in json_response:
                                    message = json_response['message'].lower()
                                    if 'another account is using' in message:
                                        result['exists'] = True
                                        username = self._extract_username_from_response(json_response)
                                        if username:
                                            result['username'] = username
                                            result['account_details'] = self._get_account_details(username)
                                        break
                                    elif any(keyword in message for keyword in ['sent', 'found', 'success']):
                                        result['exists'] = True
                                        break

                            except json.JSONDecodeError:
                                logging.error(f"JSON decode error for phone {phone_variant}")
                                continue

                    except Exception as e:
                        logging.error(f"Endpoint error for phone {phone_variant}: {str(e)}")
                        continue

                    if result['exists'] and result['username']:
                        break
                
                if result['exists'] and result['username']:
                    break

            # If account exists but no username found, try additional lookup
            if result['exists'] and not result['username']:
                try:
                    lookup_url = f"{self.base_url}/api/v1/users/lookup/"
                    lookup_data = {
                        'phone_number': phone,
                        'device_id': self.device_id,
                        'guid': str(uuid.uuid4()),
                        'waterfall_id': str(uuid.uuid4())
                    }

                    self._rate_limit()
                    lookup_response = self.session.post(
                        lookup_url,
                        headers=headers,
                        data=lookup_data,
                        proxies=self._get_random_proxy(),
                        timeout=15
                    )

                    if lookup_response.status_code == 200:
                        lookup_data = lookup_response.json()
                        if 'user' in lookup_data:
                            username = lookup_data['user'].get('username')
                            if username:
                                result['username'] = username
                                result['account_details'] = self._get_account_details(username)

                except Exception as e:
                    logging.error(f"Additional lookup error for phone {phone}: {str(e)}")

        except requests.RequestException as e:
            result['error'] = f"Request error: {str(e)}"
            logging.error(f"Request error for phone {phone}: {str(e)}")

        return result

    def print_results(self, result: Dict[str, any]) -> None:
        """Pretty print the results"""
        print("\n" + Fore.CYAN + "="*50 + Style.RESET_ALL)
        
        if 'phone' in result:
            print(Fore.YELLOW + f"Results for phone: {result['phone']}" + Style.RESET_ALL)
        elif 'username' in result:
            print(Fore.YELLOW + f"Results for @{result['username']}" + Style.RESET_ALL)
        elif 'email' in result:
            print(Fore.YELLOW + f"Results for email: {result['email']}" + Style.RESET_ALL)
            
        print(Fore.CYAN + "="*50 + Style.RESET_ALL)
        
        if result.get('error'):
            print(f"\n{Fore.RED}⚠️  Error: {result['error']}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}✓ Account exists: {result.get('exists', 'Unknown')}{Style.RESET_ALL}")
        
        if result.get('exists'):
            if result.get('username'):
                print(f"{Fore.GREEN}✓ Associated username: @{result['username']}{Style.RESET_ALL}")

            # Print account details if available
            if result.get('account_details'):
                details = result['account_details']
                print(f"\n{Fore.CYAN}Account Details:{Style.RESET_ALL}")
                if details.get('full_name'):
                    print(f"{Fore.GREEN}✓ Full name: {details['full_name']}{Style.RESET_ALL}")
                if details.get('biography'):
                    print(f"{Fore.GREEN}✓ Bio: {details['biography']}{Style.RESET_ALL}")
                if details.get('follower_count') is not None:
                    print(f"{Fore.GREEN}✓ Followers: {details['follower_count']:,}{Style.RESET_ALL}")
                if details.get('following_count') is not None:
                    print(f"{Fore.GREEN}✓ Following: {details['following_count']:,}{Style.RESET_ALL}")
                if details.get('post_count') is not None:
                    print(f"{Fore.GREEN}✓ Posts: {details['post_count']:,}{Style.RESET_ALL}")
                if details.get('is_private') is not None:
                    print(f"{Fore.GREEN}✓ Private account: {details['is_private']}{Style.RESET_ALL}")
                if details.get('is_verified') is not None:
                    print(f"{Fore.GREEN}✓ Verified account: {details['is_verified']}{Style.RESET_ALL}")
                if details.get('external_url'):
                    print(f"{Fore.GREEN}✓ Website: {details['external_url']}{Style.RESET_ALL}")
                if details.get('profile_pic_url'):
                    print(f"{Fore.GREEN}✓ Profile picture URL: {details['profile_pic_url']}{Style.RESET_ALL}")
            
            elif 'is_private' in result:
                print(f"{Fore.GREEN}✓ Private account: {result['is_private']}{Style.RESET_ALL}")
                if result.get('full_name'):
                    print(f"{Fore.GREEN}✓ Full name: {result['full_name']}{Style.RESET_ALL}")
                if result.get('follower_count'):
                    print(f"{Fore.GREEN}✓ Followers: {result['follower_count']}{Style.RESET_ALL}")
                if result.get('biography'):
                    print(f"{Fore.GREEN}✓ Bio: {result['biography']}{Style.RESET_ALL}")
                if result.get('profile_pic_url'):
                    print(f"{Fore.GREEN}✓ Profile picture URL: {result['profile_pic_url']}{Style.RESET_ALL}")
        
        if 'checked_at' in result:
            print(f"\n{Fore.BLUE}Checked at: {result['checked_at']}{Style.RESET_ALL}")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print a stylish ASCII banner for ReconGram with enhanced styling"""
    banner = f"""
        {Fore.MAGENTA}{Back.BLACK} 
        _______                                            ______                                    
        /       \                                          /      \                                  
        $$$$$$$  |  ______    _______   ______   _______  /$$$$$$  |  ______   ______   _____  ____  
        $$ |__$$ | /      \  /       | /      \ /       \ $$ | _$$/  /      \ /      \ /     \/    \ 
        $$    $$< /$$$$$$  |/$$$$$$$/ /$$$$$$  |$$$$$$$  |$$ |/    |/$$$$$$  |$$$$$$  |$$$$$$ $$$$  |
        $$$$$$$  |$$    $$ |$$ |      $$ |  $$ |$$ |  $$ |$$ |$$$$ |$$ |  $$/ /    $$ |$$ | $$ | $$ |
        $$ |  $$ |$$$$$$$$/ $$ \_____ $$ \__$$ |$$ |  $$ |$$ \__$$ |$$ |     /$$$$$$$ |$$ | $$ | $$ |
        $$ |  $$ |$$       |$$       |$$    $$/ $$ |  $$ |$$    $$/ $$ |     $$    $$ |$$ | $$ | $$ |
        $$/   $$/  $$$$$$$/  $$$$$$$/  $$$$$$/  $$/   $$/  $$$$$$/  $$/       $$$$$$$/ $$/  $$/  $$/ 

        {Fore.CYAN}----------------------------------------------------------------------------------
                                    Instagram OSINT & Recon Tool
                            Username / Email / Phone Number Checker
        -----------------------------------------------------------------------------------{Fore.RED}
        Created for educational purposes only.
        Use responsibly and ethically.
        {Style.RESET_ALL}
        """
    print(banner)

# Call the function to display the banner
print_banner()

def save_result(result: Dict[str, any]):
    """Save the result to a JSON file"""
    filename = 'instagram_osint_results.json'
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                results = json.load(f)
        else:
            results = []
        
        results.append(result)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
            
        print(f"\n{Fore.GREEN}Results saved to {filename}{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error saving results: {str(e)}{Style.RESET_ALL}")
        logging.error(f"Error saving results: {str(e)}")

def main():
    clear_screen()
    print_banner()
    
    osint = InstagramOSINT()
    
    while True:
        print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. Check Instagram username{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Check email address{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. Check phone number{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4. Exit{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.GREEN}Enter your choice (1-4): {Style.RESET_ALL}")
        
        if choice == '1':
            username = input(f"\n{Fore.GREEN}Enter Instagram username to check: @{Style.RESET_ALL}")
            
            if not username:
                print(f"\n{Fore.RED}⚠️  Username cannot be empty!{Style.RESET_ALL}")
                continue
                
            print(f"\n{Fore.YELLOW}🔍 Checking Instagram account: @{username}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Please wait...{Style.RESET_ALL}")
            
            time.sleep(random.uniform(1, 3))
            result = osint.check_username(username)
            
        elif choice == '2':
            email = input(f"\n{Fore.GREEN}Enter email address to check: {Style.RESET_ALL}")
            
            if not email:
                print(f"\n{Fore.RED}⚠️  Email cannot be empty!{Style.RESET_ALL}")
                continue
                
            print(f"\n{Fore.YELLOW}🔍 Checking email: {email}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Please wait...{Style.RESET_ALL}")
            
            time.sleep(random.uniform(1, 3))
            result = osint.check_email(email)
            
        elif choice == '3':
            phone = input(f"\n{Fore.GREEN}Enter phone number to check (with country code): {Style.RESET_ALL}")
            
            if not phone:
                print(f"\n{Fore.RED}⚠️  Phone number cannot be empty!{Style.RESET_ALL}")
                print(f"\n{Fore.RED}⚠️  Phone number cannot be empty!{Style.RESET_ALL}")
                continue
                
            print(f"\n{Fore.YELLOW}🔍 Checking phone number: {phone}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Please wait...{Style.RESET_ALL}")
            
            time.sleep(random.uniform(1, 3))
            result = osint.check_phone(phone)
            
        elif choice == '4':
            print(f"\n{Fore.GREEN}Thank you for using Instagram Advanced OSINT Tool!{Style.RESET_ALL}")
            break
            
        else:
            print(f"\n{Fore.RED}⚠️  Invalid choice! Please try again.{Style.RESET_ALL}")
            continue

        osint.print_results(result)
        save_result(result)
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        clear_screen()
        print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}Operation cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}An unexpected error occurred: {str(e)}{Style.RESET_ALL}")
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


