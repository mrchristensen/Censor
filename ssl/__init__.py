"""
Initializes ssl module. Module is to analyze OpenSSL programs to determine
if they are calling the OpenSSL libraries in a way that preservers security.
"""

from .funccall_order import FuncCallOrder

# def verify_correctness():
#     pass

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

if __name__ == "__main__":
    pass
