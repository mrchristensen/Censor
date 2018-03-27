int main()
{
    int i = 0;
    if (true)
    {
        i = 10;
        if (true)
        {
            i = 20;
            goto censor01;
        }
        i = 30;
censor01:


    }

    return 0;
}
