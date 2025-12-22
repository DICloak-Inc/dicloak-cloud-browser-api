# DICloak Cloud Browser OpenAPI 


This repository contains the official documentation  for the DICloak Browser OpenAPI , enabling programmatic control of the DICloak Antidetect Browser for multi-account management.
## 🌐 Official Website & Contact

*   **Official Website**: [https://dicloak.com/](https://dicloak.com/)
*   **Contact Email**: business@dicloak.com
*   **Social Media**:
    *   [Facebook](https://www.facebook.com/people/DICloak/61562397700474/)
    *   [Twitter (X)](https://x.com/DICloakBrowser)
    *   [LinkedIn](https://www.linkedin.com/company/dicloak-browser/)
    *   [Telegram](https://t.me/DICloakBrowser_Official)
    *   [YouTube](https://www.youtube.com/@DICloakBrowser)
    *   [Instagram](https://instagram.com/dicloak/)

## 📄 API Documentation

The full API documentation is available on the [official website](https://dicloak.com/) 

### Save Environment Configuration

**URL:** `/v2/env`  
**Method:** `POST`

#### Request Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| random_ua | bool | Yes | Randomly generate User-Agent: true: regenerate on each open, false: use first generated UA |
| random_fingerprint | bool | Yes | Random fingerprint: true: regenerate fingerprint on each open, false: use first generated fingerprint |
| proxy_update_type | string | Yes | Proxy account data update mode: COVER: overwrite, APPEND: append |
| proxy_way | string | Yes | Proxy method: NON_USE: do not use proxy (default Singapore), RANDOM: randomly select configured proxy accounts, USE_ONE: configure proxy account to be used only once |
| proxys | [proxy] | Yes | Proxy account information |
| system_type | string | No | Startup system type: WINDOW: Windows system (headed browser), LIUNX: Linux system (headless browser), Default: WINDOW |

##### Proxy Object Structure

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Proxy type (NON_USE: not use, HTTP, HTTPS, SSH, SOCKS5) |
| host | string | Yes | Proxy host |
| port | string | Yes | Proxy port |
| user_name | string | Yes | Proxy username |
| passwd | string | Yes | Proxy password |

#### Request Examples

- Modify all data
```json 
{
    "proxy_update_type" : "COVER",
    "proxy_way": "RANDOM",
    "proxys": [
        {"type": "SOCKS5","host":"ep.test.com","port":"6616","user_name":"test","passwd":"test"},
        {"type": "SOCKS5","host":"ep.test.com","port":"6616","user_name":"test","passwd":"test"},
     ],
    "random_ua": true,
    "random_fingerprint": true
} 
```
- Modify proxy data
```json 

{
    "proxy_update_type" : "COVER",
    "proxys": [
        {"type": "SOCKS5","host":"ep.test.com","port":"6616","user_name":"test","passwd":"test"},
        {"type": "SOCKS5","host":"ep.test.com","port":"6616","user_name":"test","passwd":"test"},
     ]
}
```
- Modify proxy method
```json 

{
    "proxy_way": "USE_ONE"
}
```
- Modify UA data
```json 
{
  "random_ua": true
   "ua": ""
}
```
- Modify random fingerprint
```json 

{
  "random_fingerprint": true
}
```

#### Response Example

```json 

{
    "code": 0,
    "msg": "success",
    "data": null
}
```

### Open Environment

**URL:** `/v2/env/open_env`  
**Method:** `PATCH`

#### Response Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| url | string | Yes | CDP control connection |
| session_id | string | Yes | Current CDP session ID |

#### Error Codes

| Error Code | Message | Description |
|------------|---------|-------------|
| 300104 | Proxy configuration exhausted, please update proxy configuration | When proxy_way is USE_ONE, configured proxy accounts have been used up |
| 300105 | Too many browser instances started, please close some instances and try again | Too many running instances, need to close previously unused instances |
| 300106 | Cloud browser exception | Cloud browser startup exception, please check information for judgment (commonly due to proxy information errors, unable to start) |
| 300000 | Business exception | System exception, please check information for judgment |

#### Response Example

```json 
{
    "code": 0,
    "msg": "success",
    "data": {
        "url": "ws://ip:port/cdp/c0d7fb01933d472687c04bdb47337024",
        "session_id": "c0d7fb01933d472687c04bdb47337024"
    }
}
```

### Close Environment

**URL:** `/v2/env/close_env`  
**Method:** `PATCH`

#### Response Example
```json 
{
    "code": 0,
    "msg": "success",
    "data": null
}
```

### Token Generation

**URL:** `/v2/env/generate_token`  
**Method:** `PATCH`

#### Response Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| token | string | Yes | New environment usage token |

#### Response Example
```json 
{
    "code": 0,
    "msg": "success",
    "data": {
        "token": "64CXXXX8-DCEA-4XX1-9D57-9AA1XXXX3F21"
    }
}
```

### Key Features

*   **Save Environment Configuration**: Configure browser settings like random User-Agent, random fingerprint, proxy settings, and system type (Windows/Headless Linux).
*   **Open Environment**: Launch a new browser instance with the configured settings and receive a CDP (Chrome DevTools Protocol) connection URL.
*   **Close Environment**: Terminate a specific browser instance to free up resources.
*   **Generate Token**: Create a new token for use in a new environment.


## 🛠️ Issues & Support

If you encounter any issues, have questions, or need support, please open an issue in this GitHub repository. We encourage you to provide as much detail as possible to help us resolve your problem quickly.


---
