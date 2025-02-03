# ReconGram
(Instagram OSINT Tool)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Logging](#logging)
- [Saving Results](#saving-results)
- [Disclaimer](#disclaimer)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Overview
The **Instagram OSINT Tool** is a Python-based application designed to gather information about Instagram accounts using various identifiers such as usernames, email addresses, and phone numbers. This tool is intended for educational purposes and should be used responsibly and ethically.

## Features
- **Username Check**: Verify if a specific Instagram username exists and retrieve associated account details.
- **Email Check**: Check if an email address is linked to an Instagram account and obtain the username if available.
- **Phone Number Check**: Determine if a phone number is associated with an Instagram account and retrieve the username and account details.
- **Rate Limiting**: Implemented to avoid detection and ensure compliance with Instagram's request policies.
- **Proxy Support**: Placeholder for proxy rotation to enhance anonymity during requests.
- **Logging**: All operations are logged for debugging and tracking purposes.
- **Results Saving**: Save results to a JSON file for future reference.

## Requirements
To run the Instagram OSINT Tool, you need the following:
- **Python 3.x**
- Required Python packages:
  - `requests`
    - `fake_useragent`
      - `beautifulsoup4`
        - `colorama`

## Installation
1. **Clone the repository** or download the script:
   ```bash
      git clone <repository-url>
         cd <repository-directory>
            ```

            2. **Install the required packages** using pip:
               ```bash
                  pip install requests fake_useragent beautifulsoup4 colorama
                     ```

## Usage
1. Open a terminal and navigate to the directory containing the script.
2. Run the script using Python:
   ```bash
      python app8.py
         ```

         3. Follow the on-screen prompts to check usernames, email addresses, or phone numbers.

## Examples
- **Check a Username**: Select option 1 and enter the Instagram username you want to check.
- **Check an Email**: Select option 2 and enter the email address you want to verify.
- **Check a Phone Number**: Select option 3 and enter the phone number with the country code.

## Logging
All actions and errors are logged in `instagram_osint.log`. This file can be used for troubleshooting and understanding the tool's operations.

## Saving Results
Results from the checks can be saved to a JSON file named `instagram_osint_results.json`. This allows users to keep a record of their queries for future reference.

## Disclaimer
This tool is intended for educational purposes only. Use it responsibly and ethically. Unauthorized access to accounts or data is illegal and unethical.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## Contact
For any inquiries or feedback, please contact the project maintainer at [your-email@example.com].

---

