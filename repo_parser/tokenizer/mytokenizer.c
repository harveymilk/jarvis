#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

#include <string.h>
#include <ctype.h>
#include <stdlib.h>

// build command: 
// clang -O2 -fPIC -dynamiclib \
-I"$(brew --prefix sqlite)/include" \
-L"$(brew --prefix sqlite)/lib" \
-o mytokenizer.dylib mytokenizer.c \
-lsqlite3 -undefined dynamic_lookup

// alternative build command:
// clang -O2 -fPIC -dynamiclib \
  -I/usr/include \
  -o mytokenizer.dylib mytokenizer.c \
  -lsqlite3 -undefined dynamic_lookup

typedef struct {
  char *z;
  int n;
} MyTokenizer;

static void mytok_free(MyTokenizer *p){
  if(p){ sqlite3_free(p->z); sqlite3_free(p); }
}

static int mytokCreate(void *pUnused, const char **azArg, int nArg, Fts5Tokenizer **ppOut){
  (void)pUnused; (void)azArg; (void)nArg;
  MyTokenizer *p = sqlite3_malloc(sizeof(*p));
  if(!p) return SQLITE_NOMEM;
  p->z = NULL; p->n = 0;
  *ppOut = (Fts5Tokenizer*)p;
  return SQLITE_OK;
}

static void mytokDelete(Fts5Tokenizer *pTok){
  mytok_free((MyTokenizer*)pTok);
}

static int is_alnum_utf8(unsigned char c){ return isalnum(c); }
static int is_upper(unsigned char c){ return (c>='A' && c<='Z'); }
static int is_lower(unsigned char c){ return (c>='a' && c<='z'); }

static void tolower_inplace(char *s, int n){
  for(int i=0;i<n;i++) s[i] = (char)tolower((unsigned char)s[i]);
}

static int emit_token(
  Fts5Tokenizer *pTok, const char *zToken, int nToken,
  int iStart, int iEnd, int iPos, void *pCtx,
  int (*xToken)(void*, int, const char*, int, int, int)
){
  (void)pTok; (void)iPos;
  if(nToken<=0) return SQLITE_OK;
  char *buf = sqlite3_malloc(nToken);
  if(!buf) return SQLITE_NOMEM;
  memcpy(buf, zToken, nToken);
  tolower_inplace(buf, nToken);
  int rc = xToken(pCtx, 0, buf, nToken, iStart, iEnd);
  sqlite3_free(buf);
  return rc;
}

static int mytokTokenize(
  Fts5Tokenizer *pTok, void *pCtx, int flags,
  const char *pText, int nText,
  int (*xToken)(void*, int, const char*, int, int, int)
){
  (void)pTok; (void)flags;
  int rc = SQLITE_OK;
  int i = 0;
  while(i < nText){
    while(i<nText && !is_alnum_utf8((unsigned char)pText[i])) i++;
    int start = i;
    while(i<nText && (is_alnum_utf8((unsigned char)pText[i]) || pText[i]=='_')) i++;
    int j = i;
    if(j > start){
      int segStart = start;
      for(int k=start; k<=j; k++){
        if(k==j || pText[k]=='_'){
          int segLen = k - segStart;
          if(segLen>0){
            int s = segStart;
            for(int t=segStart+1; t<=segStart+segLen; t++){
              int boundary = (t==segStart+segLen);
              if(!boundary){
                unsigned char cPrev = (unsigned char)pText[t-1];
                unsigned char cCur  = (unsigned char)pText[t];
                if(is_lower(cPrev) && is_upper(cCur)) boundary = 1;
              }
              if(boundary){
                rc = emit_token(NULL, pText + s, t - s, s, t, 0, pCtx, xToken);
                if(rc!=SQLITE_OK) return rc;
                s = t;
              }
            }
          }
          segStart = k + 1;
        }
      }
    }
  }
  return rc;
}

// Define the tokenizer structure
static const struct fts5_tokenizer sTokenizer = {
  mytokCreate, mytokDelete, mytokTokenize
};

// Register the tokenizer using the officially supported method
static int register_tokenizer(sqlite3 *db) {
  int rc;
  sqlite3_stmt *pStmt;
  struct fts5_api *pApi = NULL;
  
  // Use the officially supported method: fts5(?) + sqlite3_bind_pointer()
  rc = sqlite3_prepare_v2(db, "SELECT fts5(?)", -1, &pStmt, NULL);
  if (rc != SQLITE_OK) return rc;
  
  // Bind a pointer to get the FTS5 API
  rc = sqlite3_bind_pointer(pStmt, 1, &pApi, "fts5_api_ptr", NULL);
  if (rc != SQLITE_OK) {
    sqlite3_finalize(pStmt);
    return rc;
  }
  
  // Execute the statement to get the API
  if (sqlite3_step(pStmt) == SQLITE_ROW) {
    // pApi should now be populated
    if (pApi) {
      rc = pApi->xCreateTokenizer(pApi, "mytokenizer", NULL, (struct fts5_tokenizer*)&sTokenizer, NULL);
    } else {
      rc = SQLITE_ERROR;
    }
  } else {
    rc = SQLITE_ERROR;
  }
  
  sqlite3_finalize(pStmt);
  return rc;
}


int sqlite3_mytokenizer_init(sqlite3 *db, char **pzErrMsg,
                             const sqlite3_api_routines *pApi)
{
  SQLITE_EXTENSION_INIT2(pApi);
  (void)pzErrMsg;
  
  return register_tokenizer(db);
}
