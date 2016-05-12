#include <stdio.h>
#include "test2.h"



#ifdef A

#if B || C || ! defined (D)

#ifdef E

#endif

#endif

#endif


#ifdef C
#ifdef E

#endif

#endif

#ifdef C

#endif


/*

#ifdef SHOULD_NOT_BE_THERE


#endif

 */

//#ifdef MIKE
//int x;
//
//
//
//#if \
//  A==1 \
//  || B==2&&!C
//int y;
//
//#ifdef D
//int z;
//#endif
//
//#endif // A/B/C
//
//#endif // MIKE
//// from ABB_sub_throughput.c
//
//#    if (X==1)
//
//# else
//
//#  endif
//
//#    if (Y==1)
//
//#      else
//
//#  endif
//
//
//#ifdef _WIN32
//#include <Windows.h>
//#else
//#ifndef _WRS_KERNEL
//#include <sys/time.h>
//#else
//#include <version.h>
//
//#ifndef _WRS_VXWORKS_MAJOR
//#include <sys/times.h>
//#endif
//#endif
//#include <unistd.h>
//#endif


void f()
{

}


int main ()
{
  printf ("Nothing to see here.\n");
}
