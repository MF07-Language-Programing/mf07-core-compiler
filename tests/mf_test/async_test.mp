async intent add(a, b) {
    return a + b;
}

var t = add(2, 3);
print("ASYNC TYPE:", t);
var r = await t;
print("ASYNC_RESULT:", r);
