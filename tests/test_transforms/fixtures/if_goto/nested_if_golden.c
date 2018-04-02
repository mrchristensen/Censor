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


    }

    return 0;
}
