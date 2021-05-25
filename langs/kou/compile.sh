# npm install -g kou
kouc --wat tixy.kou --export tixy > tixy-tmp.wat
# remove unwanted js imports and unused globals
grep -vE '(import|global)' tixy-tmp.wat > tixy.wat
wat2wasm tixy.wat
