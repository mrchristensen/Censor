typedef struct
{
  int x;
  int y;
} rectangle;
rectangle mkRect(int x, int y)
{
  rectangle r = {x, y};
  return (rectangle) r;
}

int floor_double(float x)
{
  return (int) (x * 2);
}

int main()
{
  rectangle r = mkRect(3, 5);
  int i = floor_double(3.9);
  return (int) 0;
}

