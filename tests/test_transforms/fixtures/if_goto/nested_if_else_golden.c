int main()
{
    int i = 0;
    if (true)
    {
        i = 10;
        if (true)
        {
            i = 20;
            goto censor01_ENDIF;
        }

        {
            i = 30;
        }
censor01_ENDIF:


        goto censor03_ENDIF;
    }

    {
        i = 40;
        if (true)
        {
            i = 50;
            goto censor02_ENDIF;
        }

        {
            i = 60;
        }
censor02_ENDIF:


    }
censor03_ENDIF:

    return 0;
}
