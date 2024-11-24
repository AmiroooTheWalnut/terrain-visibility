#ifndef TILEDVS_H
#define TILEDVS_H

#include <stdlib.h>
#include <sys/time.h>
#include <malloc.h>
#include <fcntl.h>
#include <sys/times.h>
#include <sys/types.h>
//#include <sys/uio.h>

#include "backend/tiledMatrix.cpp"
#include <string>

typedef int elev_t; //using 4 bytes per elevation value!
//typedef short int elev_t; //using 2 bytes per elevation value!

/**; GLOBAL VARIABLES */

extern int nrows, ncols;                      // Number of rows, cols in elev.
extern int maxHeight;                       //Maximum height of elev
extern int minHeight;                       //Minimum height of elev
extern unsigned long long n;                     // nrows*ncols
extern int observer[2];			// observer coordinates


extern tiledMatrix<elev_t>* elevp; //p = pointer
extern tiledMatrix<unsigned char>* viewshedp;

extern unsigned int numBlocks, blockSizeRows, blockSizeCols;


extern int observer_ht;                /*  Ht of observer above ground (not above sea level) */
extern int target_ht;                  /*  Ht of target above ground (not above sea level) */
extern int radius;                     // Radius of interest; targets farther than this are hidden.
extern int delta[2];
extern int target[2];
extern int p[2];                       // Current point
extern int sig, pelev, v;
extern double horizon_slope, slope, s, horizon_alt;
extern int observer_alt;

extern string in_file;

extern clock_t start, endt;
extern double elapsed;

void die(const char* msg);
double read_delta_time();
void Print_Time(char* msg);
void Get_Options(const int argc, const char** const argv);
void Read_Elev();
void Calc_Vis();
void Write_Viewshed();
void run(const int argc, const char** const argv);
void Write_debug_CSV_Elev();
float ReverseFloat(const float inFloat);
int16_t reverseEndianness(int16_t value);

#endif // TILEDVS_H



