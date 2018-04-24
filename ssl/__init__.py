"""
Initializes ssl module. Module is to analyze OpenSSL programs to determine
if they are calling the OpenSSL libraries in a way that preserves security.
"""

TEST_PROGRAM = r"""
extern void a();
extern void b();
extern void d();
extern void e();
extern void f();
extern void g();

void c() {
    e();
    f();
    g();
}

int main() {
    a();
    b();
    c();


    f();
    g();

}"""
