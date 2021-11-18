# Kintsugi🍵 Testing
Adhoc Testing Framework for Kintsugi Tests

## Usage
### Geth
```
./src/executor/execute.py <Test case name> [--client-binary /path/to/geth]
```

### Nethermind
```
./src/executor/execute.py <Test case name> --client nethermind [--client-binary /path/to/dotnet] --client-working-path /path/to/Nethermind.Runner
```

## Dependencies
`requests`