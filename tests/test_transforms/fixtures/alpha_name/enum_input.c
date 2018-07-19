enum vals {here, there, anywhere};
int main(){
    enum vals place;
    place = here;
    {
        int here = 30;
        enum vals place = here;
        printf("%d\n",place);
    }
    printf("%d\n",place);
}