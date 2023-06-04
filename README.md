# LightningMailFaucet
Email Faucet, which pays Bitcoin Lightning invoices instantly.



[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<br />
<div>
  <a href="https://github.com/f418me/LightningMailFaucet">
    <img src="https://f418.me/wp-content/uploads/2023/06/offenes_netzwerk.jpg" alt="Logo" width="500" height="300">
  </a>

  <h3 align="center">LightningMailFaucet</h3>

  <p align="center">
    Python E-Mail Faucet which can pay Bitcoin Lightning invoices.
    <br />
    <br />
    <a href="https://github.com/f418me/LightningMailFaucet/issues">Report Bug</a>
    ·
    <a href="https://github.com/f418me/LightningMailFaucet/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!-- 
[![Product Name Screen Shot][product-screenshot]](https://example.com)
-->

LNbits a free and open-source lightning wallet that offers a lot of extension. 
LNbits can run on any lightning-network funding source, currently supporting LND, c-lightning, OpenNode, lntxbot, LNPay and even LNbits itself!

You can run LNbits for yourself, or easily take the service from LNBits.

Each wallet has its own API keys and there is no limit to the number of wallets you can make.

Extensions add extra functionality to LNbits so it is possible to experiment with a range of cutting-edge technologies on the lightning network. One of the extension ist LNURL-withdraw.

You can generate LNURL-withdraw links wich are also available in form of QR-Codes. With this QR-Codes every wallet that supports LNURL-withdraw can remain the amount which is defined.

Generating vouchers in large quantities by the GUI is painful. Therefore you can use this script.




<!-- GETTING STARTED -->
## Getting Started


### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/f418me/LightningMailFaucet.git
   ```
2. Install Pyhton Packages:
   ```sh
   pip install -r requirements.txt
   ```


<!-- USAGE EXAMPLES -->
### Usage
Setup an LNBits Wallet and configure the script using .env file or environment variables.
You have to config the access to the wallet and the access to a Mailbox. We use a GMail Account to send the responses.
Maybe you also like to change the design and the text of mail responses.
Than just run the script in the background.

 ```sh
   nohup python ln_mail_faucet.py &
   ```

<!-- ROADMAP -->
## Roadmap

- [ ] Add Changelog
- [ ] Docker Image
- [ ] Support of LNURLPay  
- [ ] Support for Lightning addresses  


See the [open issues](https://github.com/f418me/LightningMailFaucet/issues) for a full list of proposed features (and known issues).


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

LightningMailFaucet is released under the terms of the MIT license. See [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT) for further information.


<!-- CONTACT -->
## Contact

f418.me - [f418_me](https://twitter.com/f418_me) - info@f418.me

Project Link: [https://github.com/f418me/LNBitsVoucherGenerator](https://github.com/f418me/LightningMailFaucet)




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/f418me/LNBitsVoucherGenerator?style=for-the-badge
[contributors-url]: https://github.com/f418me/LightningMailFaucet/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/f418me/LNBitsVoucherGenerator.svg?style=for-the-badge
[forks-url]: https://github.com/f418me/LightningMailFaucet/network/members
[issues-shield]: https://img.shields.io/github/issues/f418me/LNBitsVoucherGenerator.svg?style=for-the-badge
[issues-url]: https://github.com/f418me/LightningMailFaucet/issues
[license-shield]: https://img.shields.io/github/license/f418me/LNBitsVoucherGenerator.svg?style=for-the-badge
[license-url]: https://github.com/f418me/LightningMailFaucet/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/f418-me/
[product-screenshot]: images/screenshot.png
