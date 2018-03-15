enum Color
{
  RED,
  YELLOW,
  BLUE
};
typedef enum
{
  LEFT,
  RIGHT,
  FORWARD,
  BACKWARD
} Direction;
int main()
{
  enum Color c = RED;
  enum Color *censor01 = &c;
  *censor01 = (*censor01) + 1;
  Direction d = LEFT;
  Direction *censor02 = &d;
  *censor02 = (*censor02) + 1;
}
