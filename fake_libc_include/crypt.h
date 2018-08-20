#ifndef _CRYPT_H
#define _CRYPT_H    1

#include <features.h>

/* Encrypt at most 8 characters from KEY using salt to perturb DES.  */
extern char *crypt (const char *__key, const char *__salt);

/* Setup DES tables according KEY.  */
extern void setkey (const char *__key);

/* Encrypt data in BLOCK in place if EDFLAG is zero; otherwise decrypt
   block in place.  */
extern void encrypt (char *__block, int __edflag);

#ifdef __USE_GNU
/* Reentrant versions of the functions above.  The additional argument
   points to a structure where the results are placed in.  */
struct crypt_data
  {
    char keysched[16 * 8];
    char sb0[32768];
    char sb1[32768];
    char sb2[32768];
    char sb3[32768];
    /* end-of-aligment-critical-data */
    char crypt_3_buf[14];
    char current_salt[2];
    long int current_saltbits;
    int  direction, initialized;
  };

extern char *crypt_r (const char *__key, const char *__salt,
              struct crypt_data * __restrict __data);

extern void setkey_r (const char *__key,
              struct crypt_data * __restrict __data);

extern void encrypt_r (char *__block, int __edflag,
               struct crypt_data * __restrict __data);
#endif


#endif    /* crypt.h */
