/*@ begin PerfTuning (         
  def build 
  { 
    arg build_command = 'icc -O3 -openmp -I/usr/local/icc/include -lm'; 
  } 
    
  def performance_counter          
  { 
    arg repetitions = 50; 
  }

  def performance_params 
  {
    param PERM[] = [
     ['i','j'],
#     ['j','i'],
    ];

    param U1[] = [1];
    param U2[] = [1];
    param U3[] = [1];
    param U4[] = [24];

    param IVEC1[] = [False];
    param IVEC2[] = [False];
    param SCREP[] = [False];
  }

  def search 
  { 
    arg algorithm = 'Exhaustive'; 
#    arg algorithm = 'Simplex'; 
#    arg total_runs = 1;
  } 
   
  def input_params 
  {
    param N[] = [500];
  }

  def input_vars
  {
    arg decl_file = 'decl_code.h';
    arg init_file = 'init_code.c';
  }
) @*/ 

register int i,j,k,it,jt,kt;

/*@ begin Loop (
transform Unroll(ufactor=U4)
for (k=0; k<=N-1; k++) {

  transform Composite (
  scalarreplace = (SCREP, 'double'),
  regtile = (['j'],[U1]),
  vector = (IVEC1, ['ivdep','vector always']))
    for (j=k+1; j<=N-1; j++)
      A[k][j] = A[k][j]/A[k][k];

  transform Composite (
  permut = [PERM],
  scalarreplace = (SCREP, 'double'),
  regtile = (['i','j'],[U2,U3]),
  vector = (IVEC2, ['ivdep','vector always']))
    for(i=k+1; i<=N-1; i++)
      for (j=k+1; j<=N-1; j++)
        A[i][j] = A[i][j] - A[i][k]*A[k][j];
  }
) @*/
/*@ end @*/

/*@ end @*/

