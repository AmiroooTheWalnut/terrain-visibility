/**
 * Copyright (c) 2013, Chaulio R. Ferreira, Marcus V.A. Andrade, Salles V.G. Magalhaes,
 * W. Randolph Franklin and Andre M. Pompermayer.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 *
 *   Redistributions in binary form must reproduce the above copyright notice, this
 *   list of conditions and the following disclaimer in the documentation and/or
 *   other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

 /**
  * TiledVS - Calculate an approximation to the viewshed of a specified
  * observer in a rectangular elevation matrix. This algorithm has been
  * specially designed to minimize I/O operations.
  *
  * For further information, consider the following references:
  *
  * Ferreira, C.R., et al., 2012. More efficient terrain viewshed
  * computation on massive datasets using external memory. In: Proceedings
  * of the 20th International Conference on Advances in Geographic
  * Information Systems, SIGSPATIAL ’12, Redondo Beach, California,
  * USA: ACM, 494–497.
  * Available at: http://www.ecse.rpi.edu/~wrf/p/159-acmgis2012-viewshed.pdf
  *
  * 2. Ferreira, C.R., et al. 2016, An efficient external memory algorithm
  * for terrain viewshed computation. In: ACM Transactions on Spatial
  * Algorithms and Systems 2.2 (2016): 6.
  * Available at: http://wrf.ecse.rpi.edu//p/197-chaulio-tiledvs-tsas-2016.pdf
  */

/**
 * This code is revised by Amir Mohammad Esmaieeli Sikaroudi in November 2024
 * - The global variables are moved into header files. Same for tiledMatrix.cpp and lz4.cpp.
 * - Two bytes are read instead of four bytes.
 * - The endian of the data is swapped.
 * - Cropping is fixed. Cropping only happens on one corner with minimal index.
 * - Side of terrain is guessed by reading the data twice.
 * - Height of the map is stored.
 * - Map can be dumped into CSV file for debugging.
 */



  // Uses: TiledMatrix.cpp

  // Parameters:
  // NROWS, NCOLS, OBSERVER[0], OBSERVER[1], OBSERVER_HT, RADIUS, IN_FILE, MEM_SIZE(MB), [ BLOCKSIZE_ROWS, BLOCKSIZE_COLS ]

  // Input file format: NROWS*NCOLS elev_t-size-byte elevations
  // elev_t-size is sizeof(int)(4) or sizeof(short int) (2)
  // (change it below if necessary)




// Output file format: NROWS*NCOLS bits
//  0: hidden, 1: visible.

/**; TEMPLATES */

// SQUARE   (There must be a lib with this!)

template < class C > inline C square(const C a)
{
	return a * a;
}


/**; INCLUDES.  Many of these are unnecessary, but which? */

#include "backend/TiledVS.h"
#include <cstring>
#include <cstdint>
#include <sstream>
#include <iostream>
#include <iomanip>
#include <math.h>
#include <stdio.h>

int nrows=0,ncols=0;                      // Number of rows, cols in elev.
int trueNRows=0, trueNCols=0;             // Number of rows, cols in elev for none squared inputs. messy trick
int maxHeight=-100000;                        //Maximum height of elev
int minHeight=100000;                        //Minimum height of elev
unsigned long long n=0;                     // nrows*ncols
int observer[2]={ 0 };			// observer coordinates


tiledMatrix<elev_t>* elevp=NULL; //p = pointer
tiledMatrix<unsigned char>* viewshedp=NULL;

unsigned int numBlocks=0;


int observer_ht=0;                /*  Ht of observer above ground (not above sea level) */
int target_ht=0;                  /*  Ht of target above ground (not above sea level) */
int radius=0;                     // Radius of interest; targets farther than this are hidden.
int delta[2]={ 0 };
int target[2]={ 0 };
int p[2]={ 0 };                       // Current point
int sig=0, pelev=0, v=0;
double horizon_slope=0, slope=0, s=0, horizon_alt=0;
int observer_alt=0;

string in_file="";

clock_t endt=0;
double elapsed;


unsigned int blockSizeRows = 1000;
unsigned int blockSizeCols = 1000;
clock_t start = 0;

using namespace std;




/**; TEMPLATE USING GLOBAL VARS */

// ALLOC_ARRAY.  Allocate A, an nrows x nrows 2-D array, contiguously, so it is
// also accessible as A1, a 1-D array.

template < class C > void alloc_array(C**& a, C*& a1)
{
	a = new C * [nrows];
	a1 = new C[n];
	for (int i = 0; i < nrows; i++)
		a[i] = &a1[i * ncols];
}


/**; FUNCTIONS */

// DIE

void die(const char* msg) {
	std::cerr << "ERROR: " << msg << endl;
	exit(1);
}



double read_delta_time()
{
	endt = clock();
	elapsed = ((double)(endt - start)) / CLOCKS_PER_SEC;
	start = endt;
	return elapsed;
}

/**; PRINT_TIME Print time since last call, with a message. */

void Print_Time(char* msg)
{
	// Don't bother; times are too small.
	cerr << "CPU Time for " << msg << " =" << read_delta_time() << endl;
}


/**; GET_OPTIONS  Get input options  */

void Get_Options(const int argc, const char** const argv)
{
	char* s;
	int i;

	if (argc < 8) {
		cerr << "argc=" << argc << endl;
		die
		("VIEWSHED requires 10 arguments: NROWS, NCOLS, OBSERVER[0], OBSERVER[1], OBSERVER_HT, RADIUS, IN_FILE, MEM, [ BLOCKSIZE_ROWS, BLOCKSIZE_COLS ]");
	}

    nrows = atoi(argv[1]);
    ncols = atoi(argv[2]);
	observer[0] = atoi(argv[3]);
	observer[1] = atoi(argv[4]);
	observer_ht = atoi(argv[5]);
	target_ht = observer_ht;
	radius = atoi(argv[6]);
	in_file = argv[7];
	int mem = atoi(argv[8]);

	int cellsize = sizeof(elev_t) + sizeof(unsigned char);

	if (argc > 9) { //if block size is an argument
		blockSizeCols = blockSizeRows = atoi(argv[9]);
		if (argc > 10) blockSizeCols = atoi(argv[10]);
	}
	else { //else, determine block size automatically
		blockSizeRows = ((mem * 1024 * 1024) / ncols) / cellsize;
		blockSizeCols = (double(blockSizeRows) / nrows) * ncols;

		//if blocks are too big to process efficiently, use smaller blocks
		while ((blockSizeRows * (ncols + blockSizeCols - 1) / blockSizeCols * blockSizeCols * cellsize > mem * 1024 * 1024)
			|| (blockSizeCols * (nrows + blockSizeRows - 1) / blockSizeRows * blockSizeRows * cellsize > mem * 1024 * 1024))
		{
			blockSizeRows /= 1.00001;
			blockSizeCols /= 1.00001;
		}

		//no need for blocks larger than 1000x1000
		if (blockSizeRows > 1000) blockSizeRows = 1000;
		if (blockSizeCols > 1000) blockSizeCols = 1000;
		if (blockSizeRows == 1000) blockSizeCols = (double(ncols) / nrows) * blockSizeRows;
		if (blockSizeCols == 1000) blockSizeRows = (double(nrows) / ncols) * blockSizeCols;
	}

	numBlocks = (mem * 1024 * 1024) / (cellsize * blockSizeRows * blockSizeCols);

	cerr << "VIEWSHED " << ' ' << nrows << ' ' << ncols << ' ' << observer[0]
		<< ' ' << observer[1] << ' ' << observer_ht << ' ' << radius << endl;

	cerr << "TILES: mem=" << mem << ", blockSize=[" << blockSizeRows << "," << blockSizeCols << "], numBlocks=" << numBlocks << endl;

	if (observer[0] < 0 || observer[0] >= nrows || observer[1] < 0
		|| observer[1] >= ncols)
		die("Illegal observer[0] or observer[1], out of range.");

	if (radius < 1) die("Illegal radius.");

	Print_Time((char*)"Get_Options");
}


/**; READ_ELEV */
/*
 * Read elev in the format: nrows x ncols elevations.  Put min and max into
 * elev_min and elev_max. Put location of highest point into hix, hiy.
 * All these are used only to print for interest.
 */

void Read_Elev()
{
	n = nrows * ncols;

	//extend the matrix so its size is a multiple of the block size
	int nrows_aux = ((nrows + blockSizeRows - 1) / blockSizeRows) * blockSizeRows;
	int ncols_aux = ((ncols + blockSizeCols - 1) / blockSizeCols) * blockSizeCols;
	elevp = new tiledMatrix<elev_t>(nrows_aux, ncols_aux, blockSizeRows, blockSizeCols, numBlocks, "tiles/_elev_");
    //viewshedp = new tiledMatrix<unsigned char>(nrows_aux, ncols_aux, blockSizeRows, blockSizeCols, numBlocks, "tiles/_viewshed_");
	tiledMatrix<elev_t>& elev = *elevp;

    FILE* finAgain = fopen(in_file.c_str(), "rb");
    int nreadMaxSize=0;
    elev_t* temporaryBuffer=new elev_t;
    // int test=fread(reinterpret_cast<char*>(temporaryBuffer), sizeof(elev_t), 1, finAgain);
    while(fread(reinterpret_cast<char*>(temporaryBuffer), sizeof(elev_t)/2, 1, finAgain)==1){
        nreadMaxSize=nreadMaxSize+1;
    }
    delete temporaryBuffer;
    fclose(finAgain);
    cout<<"Max int values read from file is: "<<nreadMaxSize<<endl;

    float maxRowCalValue=sqrt(nreadMaxSize);
    if(maxRowCalValue!=floor(maxRowCalValue)){
        cout<<"WARNING! THE SIZE OF CELLS IS NOT SQUARED!"<<endl;
    }
    if(nrows>maxRowCalValue){
        nrows=static_cast<int>(round(maxRowCalValue));
    }
    if(ncols>maxRowCalValue){
        ncols=static_cast<int>(round(maxRowCalValue));
    }

    int realMaxColumn=static_cast<int>(round(maxRowCalValue));

	FILE* fin = fopen(in_file.c_str(), "rb");
    int16_t* buffer = new int16_t[ncols];
	int nread;
	for (int i = 0; i < nrows; i++) {
        // int nreadSoFar=0;
        nread = fread(reinterpret_cast<char*>(buffer), 2, ncols, fin);
        // nreadSoFar=nreadSoFar+nread;
        fseek(fin,(maxRowCalValue-ncols)*2,SEEK_CUR);
        for (int j = 0; j < ncols; j++){
            int hVal=reverseEndianness(buffer[j]);
            elev.set(i, j, hVal);
            if(maxHeight<hVal){
                maxHeight=hVal;
            }
            if(minHeight>hVal){
                minHeight=hVal;
            }
        }
	}
	delete[] buffer;
	fclose(fin);

	Print_Time((char*)"Read_Elev");
}


// CALC_VIS Calculate which pixels are visible from the observer.

void Calc_Vis()
{
    delete viewshedp;
    int nrows_aux = ((nrows + blockSizeRows - 1) / blockSizeRows) * blockSizeRows;
    int ncols_aux = ((ncols + blockSizeCols - 1) / blockSizeCols) * blockSizeCols;
    viewshedp = new tiledMatrix<unsigned char>(nrows_aux, ncols_aux, blockSizeRows, blockSizeCols, numBlocks, "tiles/_viewshed_");
	int i;
	int inciny;

	const int xmin = max(observer[0] - radius, -10);
	const int ymin = max(observer[1] - radius, -10);
	const int xmax = min(observer[0] + radius, nrows + 9);
	const int ymax = min(observer[1] + radius, ncols + 9);
	const int xwidth = xmax - xmin;
	const int ywidth = ymax - ymin;
	const int perimeter = 2 * (xwidth + ywidth);  // This formula is subtle

	tiledMatrix<elev_t>& elev = *elevp;
	tiledMatrix<unsigned char>& viewshed = *viewshedp;

	viewshed.set(0);

	viewshed.set(observer[0], observer[1], 1);       // Observer is visible from itself.

	// Observer distance about sea level, incl distance above ground.
	observer_alt = elev.get(observer[0], observer[1]) + observer_ht;

	// The target is in turn every point along the smaller of the border or a box
	// of side 2*radius around the observer.

	// xmax etc are coords of pixels, not of the edges between the pixels.  I.e.,
	// xmin=5, xmax=7 means 3 pixels.
	// A 3x3 regions has a perimeter of 9.

	if (xmin == xmax || ymin == ymax)
		return;

	for (int ip = 0; ip < perimeter; ip++) {

		//define cells on square perimeter
		if (ip < ywidth) {
			target[0] = xmax;
			target[1] = ymax - ip;
		}
		else if (ip < xwidth + ywidth) {
			target[0] = xmax - (ip - ywidth);
			target[1] = ymin;
		}
		else if (ip < 2 * ywidth + xwidth) {
			target[0] = xmin;
			target[1] = ymin + (ip - xwidth - ywidth);
		}
		else {
			target[0] = xmin + (ip - 2 * ywidth - xwidth);
			target[1] = ymax;
		}

		// This occurs only when observer is on the edge of the region.
		if (observer[0] == target[0] && observer[1] == target[1])
			continue;

		// Run a line of sight out from obs to target.
		delta[0] = target[0] - observer[0];
		delta[1] = target[1] - observer[1];
		inciny = (abs(delta[0]) < abs(delta[1])); // outer parens reqd

		// Step along the coord (X or Y) that varies the most from the observer to
		// the target.  Inciny says which coord that is.  Slope is how fast the
		// other coord varies.

		slope = (double)delta[1 - inciny] / (double)delta[inciny];

		sig = (delta[inciny] > 0 ? 1 : -1);
		horizon_slope = -99999;     // Slope (in vertical plane) to horizon so far.

		// i=0 would be the observer, which is always visible.
		for (i = sig; i != delta[inciny]; i += sig) {
			p[inciny] = observer[inciny] + i;
			p[1 - inciny] = observer[1 - inciny] + (int)(i * slope);

			// Have we reached the edge of the area?
			if (p[0] < 0 || p[0] >= nrows || p[1] < 0 || p[1] >= ncols) break;

			// A little optimization, so we don't need to use long long every time (int is faster)
			if (abs(p[0] - observer[0]) + abs(p[1] - observer[1]) > radius) {
				//but sometimes we still need to use them...
				if ((square((unsigned long long)abs(p[0] - observer[0])) + square((unsigned long long)abs(p[1] - observer[1])) >
					square((unsigned long long)radius))) break;
			}

			pelev = elev.get(p[0], p[1]);

			// Slope from the observer, incl the observer_ht, to this point, at ground
			// level.  The slope is projected into the plane XZ or YZ, depending on
			// whether X or Y is varying faster, and thus being iterated thru.
			s = (double)(pelev - observer_alt) /
				(double)abs((p[inciny] - observer[inciny]));
			if (horizon_slope < s)
				horizon_slope = s;

			horizon_alt = observer_alt + horizon_slope * abs(p[inciny] - observer[inciny]);

			v = (pelev + target_ht >= horizon_alt);

			if (v) viewshed.set(p[0], p[1], 1);
		}
	}
	Print_Time((char*)"Calc_Vis");
}

/**; READ_DELTA_TIME
 * Returns time in seconds since last read_delta_time.  Automatically initializes
 * itself on 1st call and returns 0.
 */

 // WRITE_VIEWSHED Assumed to be in viewshed.  Assumed that the pixels are
 // already '0' and '1' chars, not binary 0 and 1.

void Write_Viewshed()
{
	tiledMatrix<unsigned char>& viewshed = *viewshedp;

	unsigned char mask[8] = { 128, 64, 32, 16, 8, 4, 2, 1 };      // Where each bit should go.

	char b;            // binary output 
	int i, j, idx, n;

	for (i = 0; i < nrows; i++) {
		for (j = 0; j < ncols; j++) {
			idx = i * ncols + j;
			if (idx % 8 == 0)
				b = 0;
			if (viewshed.get(i, j)) {
				b |= mask[idx & 7];
			}
			if (idx % 8 == 7)
				cout.write(&b, 1);
		}
	}
	if (idx % 8 != 7) cout.write(&b, 1);

	delete elevp;
	delete viewshedp;

	Print_Time((char*)"Write_Viewshed");
}

/**; MAIN */

/*int main(const int argc, const char** const argv)
{
	read_delta_time();           // Initialize the timer. 
	Get_Options(argc, argv);
	Read_Elev();
	Calc_Vis();
	Write_Viewshed();
}*/

/*
 * This function is added for testing the backend. It functions similar to main but allowing to be called from another code.
 */
void run(const int argc, const char** const argv) {
    read_delta_time();           // Initialize the timer.
    Get_Options(argc, argv);
    Read_Elev();
    // Write_debug_CSV_Elev();
    Calc_Vis();
    // Write_Viewshed();
}


/*
 * Convert endian for 16bit integer numbers
 */
int16_t reverseEndianness(int16_t value) {
    uint16_t unsignedValue = static_cast<uint16_t>(value); // Treat as unsigned for bit manipulation
    // uint32_t reversedUnsignedValue = ((unsignedValue >> 24) & 0x000000FF) | // Move byte 3 to byte 0
                                     // ((unsignedValue >> 8) & 0x0000FF00) | // Move byte 2 to byte 1
                                     // ((unsignedValue << 8) & 0x00FF0000) | // Move byte 1 to byte 2
                                     // ((unsignedValue << 24) & 0xFF000000); // Move byte 0 to byte 3
    uint16_t reversedUnsignedValue = ((unsignedValue >> 8) & 0x00FF) | // Move byte 1 to byte 2
                                     ((unsignedValue << 8) & 0xFF00); // Move byte 0 to byte 3
    return static_cast<int>(reversedUnsignedValue); // Cast back to signed integer
}

/*
 * This function dumps a CSV file of the elevation map.
 */
void Write_debug_CSV_Elev(){
    tiledMatrix<elev_t>& elev = *elevp;
    cout<<"Start to prepare debug text output"<<endl;

    // char start='\n';
    // cout.write(&start,1);

    ofstream myfile;
    myfile.open ("debug.csv");

    for(int i=0;i<nrows;i++){
        for(int j=0;j<ncols;j++){
            float f;
            int value=(elev.get(i,j));
            // std::memcpy (&f, &value, 4);

            // Create an output string stream
            std::ostringstream oss;

            // Set the formatting to scientific notation
            oss << std::scientific << std::setprecision(1) << value;

            // Convert the stream into a string
            std::string strVal = oss.str();
            // cout.write(strVal.c_str(),strVal.size());

            myfile << strVal.c_str();

            if(j!=ncols-1){
                char v=',';
                // cout.write(&v,1);
                myfile << v;
            }else{
                char v='\n';
                // cout.write(&v,1);
                myfile << v;
            }
        }
    }

    myfile.close();

    // cout<<""<<endl;
}
