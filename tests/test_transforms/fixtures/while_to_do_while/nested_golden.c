int main()
{
    int i = 0;
    int j = 0;
    goto censor03;
    censor04:
    {
        goto censor01;
        censor02:
            {
                j++;
                censor01:
                {
                    if (j < 10)
                        goto censor02;

                }

            }

        i++;
        censor03:
        {
            if (i < 10)
                goto censor04;

        }

    }

}

