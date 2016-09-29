# proto ext
proto => Google Protobuf
ext => Erlang External Term Format

compile protobuf to erlang ext

## Usage

```
protoc --plugin=protoc-gen-ext=CMD --ext_out=<out> <protobuf files>
```

CMD:

*   `protoext`: compile to all supported files
*   `protoext_python`: compile to python
*   `protoext_erlang`: compile to erlang

## Python

## Erlang

