int main()
{
    int i = 0;
    {
        int i = 1;
        int j = i;
    }
    int j = i;
    j++;
}