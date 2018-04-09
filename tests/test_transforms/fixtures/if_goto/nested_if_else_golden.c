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
    (void ) 0;

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
    (void ) 0;


    }
censor03_ENDIF:
    (void ) 0;

    return 0;
}
