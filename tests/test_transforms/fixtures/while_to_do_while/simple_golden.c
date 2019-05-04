int main()
{
    int i = 0;
    goto censor01;
    censor02:
    {
        i++;
        censor01:
        {
            if(i < 10)
                goto censor02;

        }

    }

}

