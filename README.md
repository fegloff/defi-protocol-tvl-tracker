# DeFi TVL Tracker

A command-line tool that extracts and displays Total Value Locked (TVL) data from multiple DeFi protocols.

## Features

- Track TVL across multiple DeFi protocols
- Filter by specific pools, token pairs, or chains
- Support for multiple data providers
- Output in different formats (table, JSON, CSV)
- Extensible architecture for adding new protocols and providers

## Installation

### Prerequisites

- Python 3.7+
- pipenv

### Setup

1. Clone the repository:

```bash
git clone harmony-one/defi-protocol-tvl-tracker
cd defi-protocol-tvl-tracker
```

2. Install dependencies using pipenv:

```bash
pipenv install
```

### Running in Development

Activate the virtual environment:

```bash
pipenv shell
```

Then run the tracker directly:

```bash
python tracker.py [options]
```

## Usage

### Basic Commands

View supported protocols:

```bash
python tracker.py --supported
```

Get TVL for a specific protocol:

```bash
python tracker.py --protocol silo
```

### Filtering Options

Filter by chain:

```bash
python tracker.py --protocol silo --chain sonic
```

Filter by token pair:

```bash
python tracker.py --protocol silo --pool S-USDC.e
```

### Output Formats

Output as a table (default):

```bash
python tracker.py --protocol silo --output table
```

Output as JSON:

```bash
python tracker.py --protocol silo --output json
```

### Advanced Usage


Disable caching to get fresh data:

```bash
python tracker.py --protocol silo --no-cache
```

## Project Structure

```
defi-tvl-tracker/
├── README.md
├── Pipfile
├── tracker.py                # Main entry point
├── src/
│   ├── __init__.py           # Package definition
│   ├── cli.py                # Command-line interface
│   ├── config.py             # Configuration settings
│   ├── providers/            # Data providers
│   │   ├── __init__.py       # Provider registry
│   │   ├── defillama.py      # DefiLlama API provider
│   │   └── ...               # Other providers implementations
│   ├── protocols/            # Protocol implementations
│   │   ├── __init__.py       # Protocol registry
│   │   ├── protocol_base.py  # Base protocol class
│   │   ├── silo.py           # Silo Finance protocol
│   │   ├── aave.py           # Aave protocol
│   │   └── ...               # Other protocol implementations
│   └── utils/
│       ├── __init__.py
│       └── formatter.py      # Output formatting utilities
```

## Adding New Protocols

To add a new protocol:

1. Create a new file in `src/protocols/` (e.g., `new_protocol.py`)
2. Implement a class inheriting from `ProtocolBase`
3. Add the protocol configuration to `config.py`

The protocol will be automatically discovered and registered.

## Adding New Providers

To add a new data provider:

1. Create a new file in `src/providers/` (e.g., `new_provider.py`)
2. Implement the provider interface
3. Register the provider in `src/providers/__init__.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.