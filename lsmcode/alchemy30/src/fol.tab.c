/* A Bison parser, made by GNU Bison 3.5.1.  */

/* Skeleton implementation for Bison GLR parsers in C

   Copyright (C) 2002-2015, 2018-2020 Free Software Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C GLR parser skeleton written by Paul Hilfinger.  */

/* Undocumented macros, especially those whose name start with YY_,
   are private implementation details.  Do not rely on them.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Bison version.  */
#define YYBISON_VERSION "3.5.1"

/* Skeleton name.  */
#define YYSKELETON_NAME "glr.c"

/* Pure parsers.  */
#define YYPURE 0






/* First part of user prologue.  */
#line 66 "../src/parser/fol.y"

#define YYSTYPE int
#define YYDEBUG 1

#include "fol.h"
#include "follex.cpp"

  // 0: no output; 1,2: increasing order of verbosity
int folDbg = 0;
//int folDbg = 1;
//int folDbg = 2;


#line 71 "fol.tab.c"

# ifndef YY_CAST
#  ifdef __cplusplus
#   define YY_CAST(Type, Val) static_cast<Type> (Val)
#   define YY_REINTERPRET_CAST(Type, Val) reinterpret_cast<Type> (Val)
#  else
#   define YY_CAST(Type, Val) ((Type) (Val))
#   define YY_REINTERPRET_CAST(Type, Val) ((Type) (Val))
#  endif
# endif
# ifndef YY_NULLPTR
#  if defined __cplusplus
#   if 201103L <= __cplusplus
#    define YY_NULLPTR nullptr
#   else
#    define YY_NULLPTR 0
#   endif
#  else
#   define YY_NULLPTR ((void*)0)
#  endif
# endif

/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token type.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    ZZ_NUM = 258,
    ZZ_DOTDOTDOT = 259,
    ZZ_STRING = 260,
    ZZ_INCLUDE = 261,
    ZZ_PREDICATE = 262,
    ZZ_FUNCTION = 263,
    ZZ_CONSTANT = 264,
    ZZ_VARIABLE = 265,
    ZZ_TYPE = 266,
    ZZ_FORALL = 267,
    ZZ_EXIST = 268,
    ZZ_EQUIV = 269,
    ZZ_IMPLY = 270
  };
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef int YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;

int yyparse (void);


/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 1
#endif

/* Default (constant) value used for initialization for null
   right-hand sides.  Unlike the standard yacc.c template, here we set
   the default value of $$ to a zeroed-out value.  Since the default
   value is undefined, this behavior is technically correct.  */
static YYSTYPE yyval_default;



#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* On compilers that do not define __PTRDIFF_MAX__ etc., make sure
   <limits.h> and (if available) <stdint.h> are included
   so that the code can choose integer types of a good width.  */

#ifndef __PTRDIFF_MAX__
# include <limits.h> /* INFRINGES ON USER NAME SPACE */
# if defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stdint.h> /* INFRINGES ON USER NAME SPACE */
#  define YY_STDINT_H
# endif
#endif

/* Narrow types that promote to a signed type and that can represent a
   signed or unsigned integer of at least N bits.  In tables they can
   save space and decrease cache pressure.  Promoting to a signed type
   helps avoid bugs in integer arithmetic.  */

#ifdef __INT_LEAST8_MAX__
typedef __INT_LEAST8_TYPE__ yytype_int8;
#elif defined YY_STDINT_H
typedef int_least8_t yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef __INT_LEAST16_MAX__
typedef __INT_LEAST16_TYPE__ yytype_int16;
#elif defined YY_STDINT_H
typedef int_least16_t yytype_int16;
#else
typedef short yytype_int16;
#endif

#if defined __UINT_LEAST8_MAX__ && __UINT_LEAST8_MAX__ <= __INT_MAX__
typedef __UINT_LEAST8_TYPE__ yytype_uint8;
#elif (!defined __UINT_LEAST8_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST8_MAX <= INT_MAX)
typedef uint_least8_t yytype_uint8;
#elif !defined __UINT_LEAST8_MAX__ && UCHAR_MAX <= INT_MAX
typedef unsigned char yytype_uint8;
#else
typedef short yytype_uint8;
#endif

#if defined __UINT_LEAST16_MAX__ && __UINT_LEAST16_MAX__ <= __INT_MAX__
typedef __UINT_LEAST16_TYPE__ yytype_uint16;
#elif (!defined __UINT_LEAST16_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST16_MAX <= INT_MAX)
typedef uint_least16_t yytype_uint16;
#elif !defined __UINT_LEAST16_MAX__ && USHRT_MAX <= INT_MAX
typedef unsigned short yytype_uint16;
#else
typedef int yytype_uint16;
#endif

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif

#ifndef YYFREE
# define YYFREE free
#endif
#ifndef YYMALLOC
# define YYMALLOC malloc
#endif
#ifndef YYREALLOC
# define YYREALLOC realloc
#endif

#define YYSIZEMAX \
  (PTRDIFF_MAX < SIZE_MAX ? PTRDIFF_MAX : YY_CAST (ptrdiff_t, SIZE_MAX))

#ifdef __cplusplus
  typedef bool yybool;
# define yytrue true
# define yyfalse false
#else
  /* When we move to stdbool, get rid of the various casts to yybool.  */
  typedef signed char yybool;
# define yytrue 1
# define yyfalse 0
#endif

#ifndef YYSETJMP
# include <setjmp.h>
# define YYJMP_BUF jmp_buf
# define YYSETJMP(Env) setjmp (Env)
/* Pacify Clang and ICC.  */
# define YYLONGJMP(Env, Val)                    \
 do {                                           \
   longjmp (Env, Val);                          \
   YY_ASSERT (0);                               \
 } while (yyfalse)
#endif

#ifndef YY_ATTRIBUTE_PURE
# if defined __GNUC__ && 2 < __GNUC__ + (96 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_PURE __attribute__ ((__pure__))
# else
#  define YY_ATTRIBUTE_PURE
# endif
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# if defined __GNUC__ && 2 < __GNUC__ + (7 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_UNUSED __attribute__ ((__unused__))
# else
#  define YY_ATTRIBUTE_UNUSED
# endif
#endif

/* The _Noreturn keyword of C11.  */
#ifndef _Noreturn
# if (defined __cplusplus \
      && ((201103 <= __cplusplus && !(__GNUC__ == 4 && __GNUC_MINOR__ == 7)) \
          || (defined _MSC_VER && 1900 <= _MSC_VER)))
#  define _Noreturn [[noreturn]]
# elif ((!defined __cplusplus || defined __clang__) \
        && (201112 <= (defined __STDC_VERSION__ ? __STDC_VERSION__ : 0)  \
            || 4 < __GNUC__ + (7 <= __GNUC_MINOR__)))
   /* _Noreturn works as-is.  */
# elif 2 < __GNUC__ + (8 <= __GNUC_MINOR__) || 0x5110 <= __SUNPRO_C
#  define _Noreturn __attribute__ ((__noreturn__))
# elif 1200 <= (defined _MSC_VER ? _MSC_VER : 0)
#  define _Noreturn __declspec (noreturn)
# else
#  define _Noreturn
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YYUSE(E) ((void) (E))
#else
# define YYUSE(E) /* empty */
#endif

#if defined __GNUC__ && ! defined __ICC && 407 <= __GNUC__ * 100 + __GNUC_MINOR__
/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                            \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")              \
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# define YY_IGNORE_MAYBE_UNINITIALIZED_END      \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif

#if defined __cplusplus && defined __GNUC__ && ! defined __ICC && 6 <= __GNUC__
# define YY_IGNORE_USELESS_CAST_BEGIN                          \
    _Pragma ("GCC diagnostic push")                            \
    _Pragma ("GCC diagnostic ignored \"-Wuseless-cast\"")
# define YY_IGNORE_USELESS_CAST_END            \
    _Pragma ("GCC diagnostic pop")
#endif
#ifndef YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_END
#endif


#define YY_ASSERT(E) ((void) (0 && (E)))

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  2
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   188

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  37
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  88
/* YYNRULES -- Number of rules.  */
#define YYNRULES  160
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  218
/* YYMAXRHS -- Maximum number of symbols on right-hand side of rule.  */
#define YYMAXRHS 10
/* YYMAXLEFT -- Maximum number of symbols to the left of a handle
   accessed by $0, $-1, etc., in any rule.  */
#define YYMAXLEFT 0

/* YYMAXUTOK -- Last valid token number (for yychar).  */
#define YYMAXUTOK   270
/* YYUNDEFTOK -- Symbol number (for yytoken) that denotes an unknown
   token.  */
#define YYUNDEFTOK  2

/* YYTRANSLATE(TOKEN-NUM) -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, with out-of-bounds checking.  */
#define YYTRANSLATE(YYX)                         \
  (0 <= (YYX) && (YYX) <= YYMAXUTOK ? yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex.  */
static const yytype_int8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
      24,     2,     2,    27,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,    20,     2,     2,     2,    23,     2,     2,
      32,    33,    21,    13,    31,    12,    26,    22,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
      36,    28,    35,    34,    25,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,    19,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,    18,     2,
       2,     2,     2,    29,     2,    30,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    14,    15,    16,
      17
};

#if YYDEBUG
/* YYRLINE[YYN] -- source line where rule number YYN was defined.  */
static const yytype_int16 yyrline[] =
{
       0,   113,   113,   115,   126,   127,   128,   129,   130,   131,
     132,   134,   136,   140,   145,   150,   139,   197,   198,   201,
     204,   214,   216,   219,   222,   224,   230,   290,   292,   303,
     301,   321,   334,   349,   354,   353,   374,   374,   374,   379,
     382,   384,   391,   397,   408,   414,   441,   406,   452,   489,
     500,   498,   507,   510,   547,   559,   560,   546,   574,   611,
     634,   659,   610,   688,   688,   694,   693,   698,   697,   700,
     701,   706,   705,   718,   717,   734,   736,   753,   756,   762,
     774,   773,   822,   830,   829,   846,   852,   897,   844,   944,
     952,   962,   963,   969,   978,   986,   995,  1007,  1016,  1031,
    1034,  1049,  1048,  1063,  1063,  1067,  1066,  1079,  1078,  1091,
    1090,  1102,  1101,  1113,  1115,  1121,  1113,  1132,  1131,  1147,
    1155,  1168,  1170,  1168,  1177,  1181,  1208,  1207,  1240,  1259,
    1240,  1425,  1442,  1441,  1601,  1615,  1629,  1646,  1663,  1676,
    1699,  1701,  1718,  1716,  1727,  1755,  1765,  1777,  1792,  1798,
    1809,  2006,  2042,  2005,  2126,  2125,  2210,  2219,  2228,  2237,
    2246
};
#endif

#if YYDEBUG || YYERROR_VERBOSE || 1
/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "$end", "error", "$undefined", "ZZ_NUM", "ZZ_DOTDOTDOT", "ZZ_STRING",
  "ZZ_INCLUDE", "ZZ_PREDICATE", "ZZ_FUNCTION", "ZZ_CONSTANT",
  "ZZ_VARIABLE", "ZZ_TYPE", "'-'", "'+'", "ZZ_FORALL", "ZZ_EXIST",
  "ZZ_EQUIV", "ZZ_IMPLY", "'v'", "'^'", "'!'", "'*'", "'/'", "'%'",
  "'\\n'", "'@'", "'.'", "'\\r'", "'='", "'{'", "'}'", "','", "'('", "')'",
  "'?'", "'>'", "'<'", "$accept", "input", "$@1", "$@2", "$@3", "at",
  "fullstop", "newline", "optnewline", "include", "nnewline",
  "type_declaration", "$@4", "is_variable_type", "constant_declarations",
  "$@5", "variable_or_string_or_constant", "constant_sep",
  "numeric_type_declaration", "$@6", "$@7", "$@8", "numeric_types",
  "single_numeric_types", "$@9", "single_numeric_type",
  "predicate_declaration", "$@10", "$@11", "$@12", "function_declaration",
  "$@13", "$@14", "$@15", "function_return_type", "types", "$@16", "$@17",
  "type_code", "$@18", "variable_code", "$@19", "exist_unique",
  "pd_not_qs", "predicate_definition", "$@20", "nothing_or_constants",
  "$@21", "function_definition", "$@22", "$@23", "$@24",
  "constants_in_groundings", "is_constant_string_num_variable",
  "function_return_constant", "weight", "sentence", "$@25", "$@26", "$@27",
  "$@28", "$@29", "$@30", "$@31", "$@32", "$@33", "$@34", "quantifier",
  "variables", "$@35", "$@36", "quant_variable", "atomic_sentence", "$@37",
  "$@38", "$@39", "nothing_or_terms", "$@40", "internal_predicate_sign",
  "asterisk", "terms", "$@41", "term", "function_term", "$@42", "$@43",
  "$@44", "internal_function_sign", YY_NULLPTR
};
#endif

#define YYPACT_NINF (-79)
#define YYTABLE_NINF (-141)

  /* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
     STATE-NUM.  */
static const yytype_int16 yypact[] =
{
     -79,    11,   -79,   -19,    45,    13,    71,   -79,   -79,   -79,
      86,    24,   -79,   -79,   -20,    94,   -20,   -20,   -20,   -79,
     -79,    28,    76,   -79,   -79,   -79,   -79,   -79,   -79,   -79,
     -79,   -79,   -79,   126,   -79,   114,   -79,   116,   -79,   -79,
     -79,   133,   -79,   -79,   -79,   -79,    39,   -79,   -79,   -79,
     141,   -79,   103,   -79,   -79,   100,    21,   121,   117,   138,
     -79,   144,   119,   -79,   -79,   122,   -79,   -79,    39,    39,
     -79,   -79,   -79,   -79,   -79,   -79,   -79,   -79,   102,   143,
     -79,   -79,   -79,   -79,   -79,   -79,    16,   -79,   -79,   128,
     128,   142,   123,   -79,    57,    72,    72,    72,    72,   -20,
     -79,   -79,   -79,   -79,   -79,   145,    44,   -79,   -79,   147,
     118,   127,   129,   -79,   130,   -79,   131,   103,   -79,   -79,
     -79,   150,   148,   -79,   -79,   -79,   -79,    39,    39,    39,
      39,   -79,   132,   -79,   -79,   -79,   135,   -79,   -79,   -79,
     -79,   139,   140,   -79,   -79,   134,   -79,   -79,   155,   -79,
     -79,   -79,   -79,   -79,     6,   -79,   -79,   146,   -79,   115,
     -79,   -18,   -79,   -79,    51,   120,   152,   -79,   -79,   -79,
     -79,   -79,   102,   102,   -79,   -79,    39,   149,   -79,   118,
     118,   -79,   -79,   -79,   -79,   -79,   137,   -79,   102,    65,
      80,   102,    66,   -79,   -79,    73,   -79,   151,   153,   154,
     -79,    67,    65,   101,   159,   -79,   169,   -79,   -79,   -79,
     -79,   -79,   -79,   -79,   170,   102,   -79,    65
};

  /* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
     Performed when YYTABLE does not specify something else to do.  Zero
     means the default is an error.  */
static const yytype_uint8 yydefact[] =
{
       2,     0,     1,     0,     0,    58,    32,    21,    17,    22,
      99,    77,     4,     5,     0,     0,     0,     0,     0,    59,
       3,     0,     0,   100,    14,    97,    96,    95,    98,    78,
      18,    79,    12,     0,    11,     0,     6,     0,     7,     8,
       9,     0,    27,    28,    26,    55,   103,    80,    10,    85,
      29,    60,     0,   117,   101,    19,   128,     0,    82,     0,
      33,     0,     0,    73,    71,    56,    69,    70,   103,   103,
     107,   105,   109,   111,    20,    15,   141,   104,     0,     0,
     119,   120,   114,    83,    81,    86,    39,    45,    61,    75,
      75,    65,     0,   118,     0,    23,    23,    23,    23,     0,
     147,   146,   151,   145,   148,     0,     0,   150,   126,     0,
       0,     0,     0,    30,    40,    34,     0,     0,    76,    74,
      72,     0,     0,    57,   102,    24,    25,   103,   103,   103,
     103,    16,     0,   149,   157,   156,     0,   158,   159,   160,
     138,   134,   135,   129,   154,   131,   125,   115,     0,   124,
      93,    92,    91,    94,    39,    89,    87,    42,    43,     0,
      46,     0,    66,    68,   108,   106,   110,   112,   152,   139,
     136,   137,     0,     0,   132,   127,   103,     0,    84,     0,
       0,    41,    37,    38,    36,    35,     0,    62,     0,   130,
     155,     0,   116,   122,    90,    39,    53,     0,     0,    49,
      52,     0,   144,     0,     0,    88,     0,    47,    50,   142,
     153,   133,   123,    48,     0,     0,    51,   143
};

  /* YYPGOTO[NTERM-NUM].  */
static const yytype_int8 yypgoto[] =
{
     -79,   -79,   -79,   -79,   -79,   -79,   -79,    -8,    33,   -79,
     -79,   -79,   -79,   -79,   -79,   -79,   -79,    88,   -79,   -79,
     -79,   -79,   -79,   -79,   -79,   -39,   -79,   -79,   -79,   -79,
     -79,   -79,   -79,   -79,   -79,    59,   -79,   -79,    56,   -79,
      62,   -79,    89,   -79,   -79,   -79,   -79,   -79,   -79,   -79,
     -79,   -79,    -2,     2,   -79,   -79,   -67,   -79,   -79,   -79,
     -79,   -79,   -79,   -79,   -79,   -79,   -79,   -79,   -17,   -79,
     -79,    38,   -79,   -79,   -79,   -79,   -79,   -79,   -79,   -79,
      -3,   -79,   -78,   -79,   -79,   -79,   -79,   -79
};

  /* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int16 yydefgoto[] =
{
      -1,     1,    10,    46,    99,    11,    75,    12,   127,    13,
      44,    14,    60,    15,    86,   159,   185,   179,    16,    61,
     116,   186,   198,   199,   214,   200,    17,    22,    52,    92,
      18,    41,    62,   117,    19,    65,   121,   122,    66,    90,
      67,    89,   119,    33,    48,    58,    84,   110,    34,    59,
     111,   180,   154,   155,    35,    24,    55,    69,    56,    96,
      95,    97,    98,    57,   109,   176,    68,    82,   147,   148,
     204,   149,    77,   145,    78,   172,   175,   191,   143,    79,
     201,   215,   202,   107,   132,   188,   173,   144
};

  /* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
     positive, shift that token.  If negative, reduce the rule whose
     number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_int16 yytable[] =
{
     106,    93,    94,    32,     7,    20,    36,     9,    38,    39,
      40,     2,     3,    91,   -13,   187,   -13,     4,   -13,   -13,
     -13,     5,     6,   -64,   -13,   -13,   -13,    25,  -140,    26,
     112,   -13,   -13,    27,    28,     7,     8,   114,     9,   178,
     112,   -31,    76,   -13,    29,   -54,   113,   114,     7,    30,
      21,     9,    42,  -113,  -113,    43,   134,   135,    31,    53,
     164,   165,   166,   167,   136,   137,   138,   139,    71,    72,
      73,    54,   140,    70,    71,    72,    73,   134,   135,   141,
     142,   -63,    70,    71,    72,    73,   137,   138,   139,    23,
     124,   131,   134,   135,   189,   190,   125,   112,   209,   126,
     210,   137,   138,   139,   114,   100,   205,   101,    45,   192,
     102,   103,   104,    63,    64,   105,    70,    71,    72,    73,
     182,   150,    37,   151,   183,   184,    74,   152,   153,   128,
     129,   130,   209,    47,   211,    80,    81,   217,    72,    73,
     196,   197,    49,    51,   -44,    50,    85,    87,   118,    83,
     108,    88,   -67,    91,   158,   133,   123,   146,    63,   156,
     157,    64,   160,   169,   168,   146,   174,   170,   171,   146,
     181,    73,   213,   196,   115,   216,   161,   162,   195,   120,
     193,   194,   206,   207,   163,   208,   177,   212,   203
};

static const yytype_uint8 yycheck[] =
{
      78,    68,    69,    11,    24,    24,    14,    27,    16,    17,
      18,     0,     1,    31,     3,    33,     5,     6,     7,     8,
       9,    10,    11,    10,    13,    14,    15,     3,     7,     5,
      24,    20,    21,     9,    10,    24,    25,    31,    27,    33,
      24,    28,    21,    32,    20,    32,    30,    31,    24,    25,
       5,    27,    24,    14,    15,    27,    12,    13,    34,    20,
     127,   128,   129,   130,    20,    21,    22,    23,    17,    18,
      19,    32,    28,    16,    17,    18,    19,    12,    13,    35,
      36,    10,    16,    17,    18,    19,    21,    22,    23,     3,
      33,    99,    12,    13,   172,   173,    24,    24,    31,    27,
      33,    21,    22,    23,    31,     3,    33,     5,    32,   176,
       8,     9,    10,    10,    11,    13,    16,    17,    18,    19,
       5,     3,    28,     5,     9,    10,    26,     9,    10,    96,
      97,    98,    31,     7,    33,    14,    15,   215,    18,    19,
       3,     4,    28,    10,     3,    29,     8,     3,    20,    32,
       7,    32,    10,    31,    24,    10,    33,    10,    10,    32,
      31,    11,    31,    28,    32,    10,    32,    28,    28,    10,
      24,    19,     3,     3,    86,   214,   117,   121,   180,    90,
      31,   179,    31,    30,   122,    31,   148,   204,   191
};

  /* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
     symbol of state STATE-NUM.  */
static const yytype_int8 yystos[] =
{
       0,    38,     0,     1,     6,    10,    11,    24,    25,    27,
      39,    42,    44,    46,    48,    50,    55,    63,    67,    71,
      24,     5,    64,     3,    92,     3,     5,     9,    10,    20,
      25,    34,    44,    80,    85,    91,    44,    28,    44,    44,
      44,    68,    24,    27,    47,    32,    40,     7,    81,    28,
      29,    10,    65,    20,    32,    93,    95,   100,    82,    86,
      49,    56,    69,    10,    11,    72,    75,    77,   103,    94,
      16,    17,    18,    19,    26,    43,    21,   109,   111,   116,
      14,    15,   104,    32,    83,     8,    51,     3,    32,    78,
      76,    31,    66,    93,    93,    97,    96,    98,    99,    41,
       3,     5,     8,     9,    10,    13,   119,   120,     7,   101,
      84,    87,    24,    30,    31,    54,    57,    70,    20,    79,
      79,    73,    74,    33,    33,    24,    27,    45,    45,    45,
      45,    44,   121,    10,    12,    13,    20,    21,    22,    23,
      28,    35,    36,   115,   124,   110,    10,   105,   106,   108,
       3,     5,     9,    10,    89,    90,    32,    31,    24,    52,
      31,    72,    75,    77,    93,    93,    93,    93,    32,    28,
      28,    28,   112,   123,    32,   113,   102,   108,    33,    54,
      88,    24,     5,     9,    10,    53,    58,    33,   122,   119,
     119,   114,    93,    31,    90,    89,     3,     4,    59,    60,
      62,   117,   119,   117,   107,    33,    31,    30,    31,    31,
      33,    33,   105,     3,    61,   118,    62,   119
};

  /* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const yytype_int8 yyr1[] =
{
       0,    37,    38,    38,    38,    38,    38,    38,    38,    38,
      38,    38,    38,    39,    40,    41,    38,    42,    42,    43,
      43,    44,    44,    45,    45,    45,    46,    47,    47,    49,
      48,    50,    50,    51,    52,    51,    53,    53,    53,    54,
      54,    54,    54,    54,    56,    57,    58,    55,    59,    59,
      61,    60,    60,    62,    64,    65,    66,    63,    63,    68,
      69,    70,    67,    71,    71,    73,    72,    74,    72,    72,
      72,    76,    75,    78,    77,    79,    79,    80,    80,    80,
      82,    81,    83,    84,    83,    86,    87,    88,    85,    89,
      89,    90,    90,    90,    90,    91,    91,    91,    91,    92,
      92,    94,    93,    95,    93,    96,    93,    97,    93,    98,
      93,    99,    93,   100,   101,   102,    93,   103,    93,   104,
     104,   106,   107,   105,   105,   108,   110,   109,   111,   112,
     109,   113,   114,   113,   115,   115,   115,   115,   115,   115,
     116,   116,   118,   117,   117,   119,   119,   119,   119,   119,
     119,   121,   122,   120,   123,   120,   124,   124,   124,   124,
     124
};

  /* YYR2[YYN] -- Number of symbols on the right hand side of rule YYN.  */
static const yytype_int8 yyr2[] =
{
       0,     2,     0,     3,     2,     2,     3,     3,     3,     3,
       4,     3,     3,     0,     0,     0,     8,     1,     2,     0,
       1,     1,     1,     0,     1,     1,     3,     1,     1,     0,
       6,     1,     1,     0,     0,     4,     1,     1,     1,     0,
       1,     3,     2,     2,     0,     0,     0,    10,     3,     1,
       0,     4,     1,     1,     0,     0,     0,     7,     1,     0,
       0,     0,     8,     1,     1,     0,     4,     0,     4,     1,
       1,     0,     3,     0,     3,     0,     1,     0,     1,     1,
       0,     3,     0,     0,     4,     0,     0,     0,     9,     1,
       3,     1,     1,     1,     1,     1,     1,     1,     1,     0,
       1,     0,     4,     0,     2,     0,     5,     0,     5,     0,
       5,     0,     5,     0,     0,     0,     6,     0,     3,     1,
       1,     0,     0,     5,     1,     1,     0,     4,     0,     0,
       5,     0,     0,     4,     1,     1,     2,     2,     1,     2,
       0,     1,     0,     4,     1,     1,     1,     1,     1,     2,
       1,     0,     0,     6,     0,     4,     1,     1,     1,     1,
       1
};


/* YYDPREC[RULE-NUM] -- Dynamic precedence of rule #RULE-NUM (0 if none).  */
static const yytype_int8 yydprec[] =
{
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     1,     0,     1,     0,
       1,     0,     1,     0,     0,     0,     2,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0
};

/* YYMERGER[RULE-NUM] -- Index of merging function for rule #RULE-NUM.  */
static const yytype_int8 yymerger[] =
{
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0
};

/* YYIMMEDIATE[RULE-NUM] -- True iff rule #RULE-NUM is not to be deferred, as
   in the case of predicates.  */
static const yybool yyimmediate[] =
{
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0
};

/* YYCONFLP[YYPACT[STATE-NUM]] -- Pointer into YYCONFL of start of
   list of conflicting reductions corresponding to action entry for
   state STATE-NUM in yytable.  0 means no conflicts.  The list in
   yyconfl is terminated by a rule number of 0.  */
static const yytype_int8 yyconflp[] =
{
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     1,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,    19,    21,    23,    25,     0,     0,     0,     3,
       0,     0,     9,    11,     0,     0,     0,     0,     0,     0,
       0,    13,    15,    17,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     5,
       0,     0,     0,     0,     0,     0,     0,     7,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,    27,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0
};

/* YYCONFL[I] -- lists of conflicting rule numbers, each terminated by
   0, pointed into by YYCONFLP.  */
static const short yyconfl[] =
{
       0,    13,     0,    99,     0,    82,     0,   121,     0,   155,
       0,   155,     0,   155,     0,   155,     0,   155,     0,   116,
       0,   116,     0,   116,     0,   116,     0,   121,     0
};

/* Error token number */
#define YYTERROR 1



YYSTYPE yylval;

int yynerrs;
int yychar;

static const int YYEOF = 0;
static const int YYEMPTY = -2;

typedef enum { yyok, yyaccept, yyabort, yyerr } YYRESULTTAG;

#define YYCHK(YYE)                              \
  do {                                          \
    YYRESULTTAG yychk_flag = YYE;               \
    if (yychk_flag != yyok)                     \
      return yychk_flag;                        \
  } while (0)

#if YYDEBUG

# ifndef YYFPRINTF
#  define YYFPRINTF fprintf
# endif

# define YY_FPRINTF                             \
  YY_IGNORE_USELESS_CAST_BEGIN YY_FPRINTF_

# define YY_FPRINTF_(Args)                      \
  do {                                          \
    YYFPRINTF Args;                             \
    YY_IGNORE_USELESS_CAST_END                  \
  } while (0)

# define YY_DPRINTF                             \
  YY_IGNORE_USELESS_CAST_BEGIN YY_DPRINTF_

# define YY_DPRINTF_(Args)                      \
  do {                                          \
    if (yydebug)                                \
      YYFPRINTF Args;                           \
    YY_IGNORE_USELESS_CAST_END                  \
  } while (0)

/* This macro is provided for backward compatibility. */
#ifndef YY_LOCATION_PRINT
# define YY_LOCATION_PRINT(File, Loc) ((void) 0)
#endif



/*-----------------------------------.
| Print this symbol's value on YYO.  |
`-----------------------------------*/

static void
yy_symbol_value_print (FILE *yyo, int yytype, YYSTYPE const * const yyvaluep)
{
  FILE *yyoutput = yyo;
  YYUSE (yyoutput);
  if (!yyvaluep)
    return;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YYUSE (yytype);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/*---------------------------.
| Print this symbol on YYO.  |
`---------------------------*/

static void
yy_symbol_print (FILE *yyo, int yytype, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyo, "%s %s (",
             yytype < YYNTOKENS ? "token" : "nterm", yytname[yytype]);

  yy_symbol_value_print (yyo, yytype, yyvaluep);
  YYFPRINTF (yyo, ")");
}

# define YY_SYMBOL_PRINT(Title, Type, Value, Location)                  \
  do {                                                                  \
    if (yydebug)                                                        \
      {                                                                 \
        YY_FPRINTF ((stderr, "%s ", Title));                            \
        yy_symbol_print (stderr, Type, Value);        \
        YY_FPRINTF ((stderr, "\n"));                                    \
      }                                                                 \
  } while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;

struct yyGLRStack;
static void yypstack (struct yyGLRStack* yystackp, ptrdiff_t yyk)
  YY_ATTRIBUTE_UNUSED;
static void yypdumpstack (struct yyGLRStack* yystackp)
  YY_ATTRIBUTE_UNUSED;

#else /* !YYDEBUG */

# define YY_DPRINTF(Args) do {} while (yyfalse)
# define YY_SYMBOL_PRINT(Title, Type, Value, Location)

#endif /* !YYDEBUG */

/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   SIZE_MAX < YYMAXDEPTH * sizeof (GLRStackItem)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif

/* Minimum number of free items on the stack allowed after an
   allocation.  This is to allow allocation and initialization
   to be completed by functions that call yyexpandGLRStack before the
   stack is expanded, thus insuring that all necessary pointers get
   properly redirected to new data.  */
#define YYHEADROOM 2

#ifndef YYSTACKEXPANDABLE
#  define YYSTACKEXPANDABLE 1
#endif

#if YYSTACKEXPANDABLE
# define YY_RESERVE_GLRSTACK(Yystack)                   \
  do {                                                  \
    if (Yystack->yyspaceLeft < YYHEADROOM)              \
      yyexpandGLRStack (Yystack);                       \
  } while (0)
#else
# define YY_RESERVE_GLRSTACK(Yystack)                   \
  do {                                                  \
    if (Yystack->yyspaceLeft < YYHEADROOM)              \
      yyMemoryExhausted (Yystack);                      \
  } while (0)
#endif


#if YYERROR_VERBOSE

# ifndef yystpcpy
#  if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
yystpcpy (char *yydest, const char *yysrc)
{
  char *yyd = yydest;
  const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif

# ifndef yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static ptrdiff_t
yytnamerr (char *yyres, const char *yystr)
{
  if (*yystr == '"')
    {
      ptrdiff_t yyn = 0;
      char const *yyp = yystr;

      for (;;)
        switch (*++yyp)
          {
          case '\'':
          case ',':
            goto do_not_strip_quotes;

          case '\\':
            if (*++yyp != '\\')
              goto do_not_strip_quotes;
            else
              goto append;

          append:
          default:
            if (yyres)
              yyres[yyn] = *yyp;
            yyn++;
            break;

          case '"':
            if (yyres)
              yyres[yyn] = '\0';
            return yyn;
          }
    do_not_strip_quotes: ;
    }

  if (yyres)
    return yystpcpy (yyres, yystr) - yyres;
  else
    return YY_CAST (ptrdiff_t, strlen (yystr));
}
# endif

#endif /* !YYERROR_VERBOSE */

/** State numbers. */
typedef int yyStateNum;

/** Rule numbers. */
typedef int yyRuleNum;

/** Grammar symbol. */
typedef int yySymbol;

/** Item references. */
typedef short yyItemNum;

typedef struct yyGLRState yyGLRState;
typedef struct yyGLRStateSet yyGLRStateSet;
typedef struct yySemanticOption yySemanticOption;
typedef union yyGLRStackItem yyGLRStackItem;
typedef struct yyGLRStack yyGLRStack;

struct yyGLRState {
  /** Type tag: always true.  */
  yybool yyisState;
  /** Type tag for yysemantics.  If true, yysval applies, otherwise
   *  yyfirstVal applies.  */
  yybool yyresolved;
  /** Number of corresponding LALR(1) machine state.  */
  yyStateNum yylrState;
  /** Preceding state in this stack */
  yyGLRState* yypred;
  /** Source position of the last token produced by my symbol */
  ptrdiff_t yyposn;
  union {
    /** First in a chain of alternative reductions producing the
     *  nonterminal corresponding to this state, threaded through
     *  yynext.  */
    yySemanticOption* yyfirstVal;
    /** Semantic value for this state.  */
    YYSTYPE yysval;
  } yysemantics;
};

struct yyGLRStateSet {
  yyGLRState** yystates;
  /** During nondeterministic operation, yylookaheadNeeds tracks which
   *  stacks have actually needed the current lookahead.  During deterministic
   *  operation, yylookaheadNeeds[0] is not maintained since it would merely
   *  duplicate yychar != YYEMPTY.  */
  yybool* yylookaheadNeeds;
  ptrdiff_t yysize;
  ptrdiff_t yycapacity;
};

struct yySemanticOption {
  /** Type tag: always false.  */
  yybool yyisState;
  /** Rule number for this reduction */
  yyRuleNum yyrule;
  /** The last RHS state in the list of states to be reduced.  */
  yyGLRState* yystate;
  /** The lookahead for this reduction.  */
  int yyrawchar;
  YYSTYPE yyval;
  /** Next sibling in chain of options.  To facilitate merging,
   *  options are chained in decreasing order by address.  */
  yySemanticOption* yynext;
};

/** Type of the items in the GLR stack.  The yyisState field
 *  indicates which item of the union is valid.  */
union yyGLRStackItem {
  yyGLRState yystate;
  yySemanticOption yyoption;
};

struct yyGLRStack {
  int yyerrState;


  YYJMP_BUF yyexception_buffer;
  yyGLRStackItem* yyitems;
  yyGLRStackItem* yynextFree;
  ptrdiff_t yyspaceLeft;
  yyGLRState* yysplitPoint;
  yyGLRState* yylastDeleted;
  yyGLRStateSet yytops;
};

#if YYSTACKEXPANDABLE
static void yyexpandGLRStack (yyGLRStack* yystackp);
#endif

_Noreturn static void
yyFail (yyGLRStack* yystackp, const char* yymsg)
{
  if (yymsg != YY_NULLPTR)
    yyerror (yymsg);
  YYLONGJMP (yystackp->yyexception_buffer, 1);
}

_Noreturn static void
yyMemoryExhausted (yyGLRStack* yystackp)
{
  YYLONGJMP (yystackp->yyexception_buffer, 2);
}

#if YYDEBUG || YYERROR_VERBOSE
/** A printable representation of TOKEN.  */
static inline const char*
yytokenName (yySymbol yytoken)
{
  return yytoken == YYEMPTY ? "" : yytname[yytoken];
}
#endif

/** Fill in YYVSP[YYLOW1 .. YYLOW0-1] from the chain of states starting
 *  at YYVSP[YYLOW0].yystate.yypred.  Leaves YYVSP[YYLOW1].yystate.yypred
 *  containing the pointer to the next state in the chain.  */
static void yyfillin (yyGLRStackItem *, int, int) YY_ATTRIBUTE_UNUSED;
static void
yyfillin (yyGLRStackItem *yyvsp, int yylow0, int yylow1)
{
  int i;
  yyGLRState *s = yyvsp[yylow0].yystate.yypred;
  for (i = yylow0-1; i >= yylow1; i -= 1)
    {
#if YYDEBUG
      yyvsp[i].yystate.yylrState = s->yylrState;
#endif
      yyvsp[i].yystate.yyresolved = s->yyresolved;
      if (s->yyresolved)
        yyvsp[i].yystate.yysemantics.yysval = s->yysemantics.yysval;
      else
        /* The effect of using yysval or yyloc (in an immediate rule) is
         * undefined.  */
        yyvsp[i].yystate.yysemantics.yyfirstVal = YY_NULLPTR;
      s = yyvsp[i].yystate.yypred = s->yypred;
    }
}


/** If yychar is empty, fetch the next token.  */
static inline yySymbol
yygetToken (int *yycharp)
{
  yySymbol yytoken;
  if (*yycharp == YYEMPTY)
    {
      YY_DPRINTF ((stderr, "Reading a token: "));
      *yycharp = yylex ();
    }
  if (*yycharp <= YYEOF)
    {
      *yycharp = yytoken = YYEOF;
      YY_DPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yytoken = YYTRANSLATE (*yycharp);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }
  return yytoken;
}

/* Do nothing if YYNORMAL or if *YYLOW <= YYLOW1.  Otherwise, fill in
 * YYVSP[YYLOW1 .. *YYLOW-1] as in yyfillin and set *YYLOW = YYLOW1.
 * For convenience, always return YYLOW1.  */
static inline int yyfill (yyGLRStackItem *, int *, int, yybool)
     YY_ATTRIBUTE_UNUSED;
static inline int
yyfill (yyGLRStackItem *yyvsp, int *yylow, int yylow1, yybool yynormal)
{
  if (!yynormal && yylow1 < *yylow)
    {
      yyfillin (yyvsp, *yylow, yylow1);
      *yylow = yylow1;
    }
  return yylow1;
}

/** Perform user action for rule number YYN, with RHS length YYRHSLEN,
 *  and top stack item YYVSP.  YYLVALP points to place to put semantic
 *  value ($$), and yylocp points to place for location information
 *  (@$).  Returns yyok for normal return, yyaccept for YYACCEPT,
 *  yyerr for YYERROR, yyabort for YYABORT.  */
static YYRESULTTAG
yyuserAction (yyRuleNum yyn, int yyrhslen, yyGLRStackItem* yyvsp,
              yyGLRStack* yystackp,
              YYSTYPE* yyvalp)
{
  yybool yynormal YY_ATTRIBUTE_UNUSED = yystackp->yysplitPoint == YY_NULLPTR;
  int yylow;
  YYUSE (yyvalp);
  YYUSE (yyrhslen);
# undef yyerrok
# define yyerrok (yystackp->yyerrState = 0)
# undef YYACCEPT
# define YYACCEPT return yyaccept
# undef YYABORT
# define YYABORT return yyabort
# undef YYERROR
# define YYERROR return yyerrok, yyerr
# undef YYRECOVERING
# define YYRECOVERING() (yystackp->yyerrState != 0)
# undef yyclearin
# define yyclearin (yychar = YYEMPTY)
# undef YYFILL
# define YYFILL(N) yyfill (yyvsp, &yylow, (N), yynormal)
# undef YYBACKUP
# define YYBACKUP(Token, Value)                                              \
  return yyerror (YY_("syntax error: cannot back up")),     \
         yyerrok, yyerr

  yylow = 1;
  if (yyrhslen == 0)
    *yyvalp = yyval_default;
  else
    *yyvalp = yyvsp[YYFILL (1-yyrhslen)].yystate.yysemantics.yysval;
  switch (yyn)
    {
  case 2:
#line 113 "../src/parser/fol.y"
  { if (folDbg >= 2) printf("input: empty\n"); }
#line 1219 "fol.tab.c"
    break;

  case 3:
#line 116 "../src/parser/fol.y"
  { 
    yyerrok; // tell Bison not to suppress any errors
    const char* tok; 
    while (true)
    {
      tok = zztokenList.removeLast();
      if (strcmp(tok,"\n")==0) { delete tok; break; }
      delete tok;
    }
  }
#line 1234 "fol.tab.c"
    break;

  case 13:
#line 140 "../src/parser/fol.y"
  { 
    if (folDbg >= 2) printf("input: weight\n"); 
    zzreset();
  }
#line 1243 "fol.tab.c"
    break;

  case 14:
#line 145 "../src/parser/fol.y"
  {  
    if (folDbg >= 2) printf("input: sentence\n");
      // the states should be reset because a parse error may have occurred
  }
#line 1252 "fol.tab.c"
    break;

  case 15:
#line 150 "../src/parser/fol.y"
  {

    ListObj* formula;
    zzassert(zzoldNewVarList.size()==0,"expected zzoldNewVarList.size()==0");
    zzassert(zzformulaListObjs.size()==1,"expected zzformulaListObjs.size()=1");
   	formula = zzformulaListObjs.top(); zzformulaListObjs.pop();

   	zzdetermineEqPredTypes(formula);//set the any unknown type of '=' predicates
    zzeqPredList.clear();
   	zzdetermineIntPredTypes(formula);//set the any unknown type of internal predicates
    zzintPredList.clear();
   	zzdetermineIntFuncTypes(formula);//set the any unknown type of internal functions
    zzintFuncList.clear();
    zzsetPlusVarTypeId();// set typeIds of variables with pluses before them
    zzcheckVarNameToIdMap();
    
    if (zzhasFullStop && zzwt != NULL)
    {
      zzerr("A weight must not be specified for a formula that is "
            "terminated with a period (i.e. the formula is hard).");
      delete zzwt; zzwt = NULL;
    }
	
      // at this point we are sure we are dealing with a formula

      //if there are errors, we can keep this formula for further processing
    if (zznumErrors == 0)
    {
        //defer converting the formula to CNF until we have read all the
        //.db files and are sure that we know all the constants to ground
        //formula's clauses
      ZZFormulaInfo* epfi 
        = new ZZFormulaInfo(formula, zzformulaStr, zzfdnumPreds, zzwt, 
                            zzdefaultWt, zzdomain, zzmln, zzvarNameToIdMap, 
                            zzplusVarMap, zznumAsterisk,
                            zzhasFullStop, zzreadHardClauseWts, 
                            zzmustHaveWtOrFullStop);
      zzformulaInfos.append(epfi); 
    }

    if (zzwt) { delete zzwt; zzwt = NULL; }
  }
#line 1299 "fol.tab.c"
    break;

  case 17:
#line 197 "../src/parser/fol.y"
         { zzconsumeToken(zztokenList,"@"); }
#line 1305 "fol.tab.c"
    break;

  case 18:
#line 198 "../src/parser/fol.y"
         { zzconsumeToken(zztokenList,"@"); }
#line 1311 "fol.tab.c"
    break;

  case 20:
#line 205 "../src/parser/fol.y"
{ 
  if (folDbg >= 1) printf(".\n"); zzconsumeToken(zztokenList,"."); 
  zzassert(!zzhasFullStop, "expecting no full stop");
  zzhasFullStop = true;
  zzformulaStr.append(".");
}
#line 1322 "fol.tab.c"
    break;

  case 21:
#line 214 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("\\n\n"); zzconsumeToken(zztokenList,"\n"); }
#line 1328 "fol.tab.c"
    break;

  case 22:
#line 216 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("\\r\n"); zzconsumeToken(zztokenList,"\r"); }
#line 1334 "fol.tab.c"
    break;

  case 24:
#line 222 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("\\n\n"); zzconsumeToken(zztokenList,"\n"); }
#line 1340 "fol.tab.c"
    break;

  case 25:
#line 224 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("\\r\n"); zzconsumeToken(zztokenList,"\r"); }
#line 1346 "fol.tab.c"
    break;

  case 26:
#line 231 "../src/parser/fol.y"
{
  const char* inc = zztokenList.removeLast();
  const char* str = zztokenList.removeLast();
  const char* nl = zztokenList.removeLast();
  zzassert(strcmp(inc,"#include")==0,"expecting #include keyword");

  if (folDbg >= 1) printf("#include %s ", str);

  string s(str);
  if (s.length() == 0)
  {
    zzerr("empty string used with #include");
    delete [] inc;
    delete [] str;
    delete [] nl;
    break;
  }

  zzassert(s.at(0) == '"' && s.at(s.length()-1) == '"', "no enclosing \"");
  s = s.substr(1, s.length()-2);
  int len = s.length();

  // if it is a .cpp file, then we are dealing with linked-in functions and predicates
  if (s.at(len-4)=='.' && s.at(len-3)=='c' && s.at(len-2)=='p' &&
	  s.at(len-1)=='p')
  {
    zzcompileFunctions(str);
    zzusingLinkedPredicates = true;    
    zzusingLinkedFunctions = true;    
    break;
  }

  FILE* newin = fopen(s.c_str(), "r" );
  if (newin)
  {
    zzinStack.push(ZZFileState(yyin, string(zzinFileName), zznumCharRead, 
                               zzline, zzcolumn)); 
    ungetc('\n', newin); // pretend that file begins with a newline
    zzline = 1;
    zzcolumn = -1;
    zzline--;
    zzinFileName = str;
    yyrestart(newin); 
    zznumCharRead = 0;

      // if it is a .db file containing ground predicates
    if ((s.at(len-3)=='.' && s.at(len-2)=='d' && s.at(len-1)=='b'))
      zzparseGroundPred = true;
  } 
  else
    zzerr("Failed to open file %s.", str);
  
  delete [] inc;
  delete [] str;
  delete [] nl;
}
#line 1407 "fol.tab.c"
    break;

  case 27:
#line 290 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("\\n\n"); }
#line 1413 "fol.tab.c"
    break;

  case 28:
#line 292 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("\\r\n"); }
#line 1419 "fol.tab.c"
    break;

  case 29:
#line 303 "../src/parser/fol.y"
{ 
  zzconsumeToken(zztokenList,"=");
  zzconsumeToken(zztokenList,"{");
  if (folDbg >= 1) printf("= { "); 
  if (folDbg >= 2) printf("type_declarations: constant_declarations\n");
}
#line 1430 "fol.tab.c"
    break;

  case 30:
#line 311 "../src/parser/fol.y"
{
  if (folDbg >= 1) printf("} ");           
  zzconsumeToken(zztokenList, "}");
  delete [] zztypeName;
  zztypeName = NULL;
}
#line 1441 "fol.tab.c"
    break;

  case 31:
#line 322 "../src/parser/fol.y"
{
  const char* idf = zztokenList.removeLast();
  if (folDbg >= 1) printf("type t_%s ", idf);
  zzassert(!zzdomain->isType(idf), "expecting type to be undefined");
  int id = zzaddTypeToDomain(zzdomain, idf);
  zzassert(id >= 0,"expecting id >= 0");
  zzassert(zztypeName==NULL,"expecting zztypeName==NULL");
  zztypeName = new char[strlen(idf)+1];
  strcpy(zztypeName, idf);
  delete [] idf;
}
#line 1457 "fol.tab.c"
    break;

  case 32:
#line 335 "../src/parser/fol.y"
{
  const char* idf = zztokenList.removeLast();
  if (folDbg >= 1) printf("type t_%s ", idf);
  zzassert(zzdomain->isType(idf),"expecting type to be defined");
  //zzwarn("Type %s has been declared before.",idf);
  zzassert(zztypeName==NULL,"expecting zztypeName==NULL");
  zztypeName = new char[strlen(idf)+1];
  strcpy(zztypeName, idf);
  delete [] idf;
}
#line 1472 "fol.tab.c"
    break;

  case 34:
#line 354 "../src/parser/fol.y"
  { if (folDbg >= 2) printf("constant_declarations: ZZ_VARIABLE\n"); }
#line 1478 "fol.tab.c"
    break;

  case 35:
#line 356 "../src/parser/fol.y"
  {
    const char* vsc = zztokenList.removeLast();
    if (folDbg >= 1) printf("cd_%s ", vsc);
    int constId = zzdomain->getConstantId(vsc);
    if (constId < 0)
      zzaddConstantToDomain(vsc, zztypeName);
    else
    {
      const char* prevType = zzdomain->getConstantTypeName(constId);
      if (strcmp(prevType,zztypeName)!=0)
        zzerr("constant %s previously declared to be of type %s is redeclared "
              "to be of type %s", vsc, prevType, zztypeName);
    }
    delete [] vsc;
  }
#line 1498 "fol.tab.c"
    break;

  case 40:
#line 382 "../src/parser/fol.y"
       { zzconsumeToken(zztokenList, ","); }
#line 1504 "fol.tab.c"
    break;

  case 41:
#line 385 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"\n");
    zzconsumeToken(zztokenList,",");
    zzconsumeToken(zztokenList,"\n");
  }
#line 1514 "fol.tab.c"
    break;

  case 42:
#line 392 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"\n");
    zzconsumeToken(zztokenList,",");
  }
#line 1523 "fol.tab.c"
    break;

  case 43:
#line 398 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,",");
    zzconsumeToken(zztokenList,"\n");
  }
#line 1532 "fol.tab.c"
    break;

  case 44:
#line 408 "../src/parser/fol.y"
{
  if (folDbg >= 2) printf("numeric_type_declarations: \n");
  zzconsumeToken(zztokenList,"=");
  zzconsumeToken(zztokenList,"{");  
}
#line 1542 "fol.tab.c"
    break;

  case 45:
#line 414 "../src/parser/fol.y"
{
  const char* numStr = zztokenList.removeLast();
  if (folDbg >= 1) printf(" %s ", numStr);
  
  double d = atof(numStr);
  zzinitialNumDeclaration = int(d);
  if (d != zzinitialNumDeclaration) zzerr("constant %s must be an integer", numStr);

  char constStr[100];
  zzcreateIntConstant(constStr, zztypeName, zzinitialNumDeclaration);
  int constId = zzdomain->getConstantId(constStr);
  if (constId < 0) 
    zzaddConstantToDomain(constStr, zztypeName);
  else
  {
    const char* prevType = zzdomain->getConstantTypeName(constId);
    if (strcmp(prevType,zztypeName)!=0)
    {
      char buf[30]; sprintf(buf, "%d", zzinitialNumDeclaration);
      zzerr("constant %s previously declared to be of type %s is redeclared "
            "to be of type %s", buf, prevType, zztypeName);        
    }
  }

  delete [] numStr;
}
#line 1573 "fol.tab.c"
    break;

  case 46:
#line 441 "../src/parser/fol.y"
{
  zzconsumeToken(zztokenList, ",");
}
#line 1581 "fol.tab.c"
    break;

  case 47:
#line 446 "../src/parser/fol.y"
{
  zzconsumeToken(zztokenList, "}");
}
#line 1589 "fol.tab.c"
    break;

  case 48:
#line 453 "../src/parser/fol.y"
{
  //const char* numStr1 = zztokenList.removeLast();
  zzconsumeToken(zztokenList, "...");
  zzconsumeToken(zztokenList, ",");
  const char* numStr2 = zztokenList.removeLast();
  if (folDbg >= 1) printf("= ... , %s } ", numStr2);
  
  double d2 = atof(numStr2);
  int i2 = int(d2);
  if (d2 != i2) zzerr("constant %s must be an integer", numStr2);
  if (zzinitialNumDeclaration > i2)
    zzerr("first constant cannot be larger than last constant %s", numStr2);

  for (int i = zzinitialNumDeclaration + 1; i <= i2; i++)
  {
    char constStr[100];
    zzcreateIntConstant(constStr, zztypeName, i);
    int constId = zzdomain->getConstantId(constStr);
    if (constId < 0) 
      zzaddConstantToDomain(constStr, zztypeName);
    else
    {
      const char* prevType = zzdomain->getConstantTypeName(constId);
      if (strcmp(prevType,zztypeName)!=0)
      {
        char buf[30]; sprintf(buf, "%d", i);
        zzerr("constant %s previously declared to be of type %s is redeclared "
              "to be of type %s", buf, prevType, zztypeName);        
      }
    }
  }

  delete [] numStr2; delete [] zztypeName;
  zztypeName = NULL;
}
#line 1629 "fol.tab.c"
    break;

  case 49:
#line 490 "../src/parser/fol.y"
{
  delete [] zztypeName;
  zztypeName = NULL;
}
#line 1638 "fol.tab.c"
    break;

  case 50:
#line 500 "../src/parser/fol.y"
  {  
    zzconsumeToken(zztokenList, ",");
    if (folDbg >= 1) printf(", "); 
    if (folDbg >= 2) printf("single_numeric_types: single_numeric_type\n"); 
  }
#line 1648 "fol.tab.c"
    break;

  case 53:
#line 511 "../src/parser/fol.y"
{
  const char* numStr = zztokenList.removeLast();
  if (folDbg >= 1) printf(" %s ", numStr);
  
  double d = atof(numStr);
  int i = int(d);
  if (d != i) zzerr("constant %s must be an integer", numStr);

  char constStr[100];
  zzcreateIntConstant(constStr, zztypeName, i);
  int constId = zzdomain->getConstantId(constStr);
  if (constId < 0) 
    zzaddConstantToDomain(constStr, zztypeName);
  else
  {
    const char* prevType = zzdomain->getConstantTypeName(constId);
    if (strcmp(prevType,zztypeName) != 0)
    {
      char buf[30]; sprintf(buf, "%d", i);
      zzerr("constant %s previously declared to be of type %s is redeclared "
            "to be of type %s", buf, prevType, zztypeName);        
    }
  }

  delete [] numStr;
}
#line 1679 "fol.tab.c"
    break;

  case 54:
#line 547 "../src/parser/fol.y"
{
  const char* predName = zztokenList.removeLast();

  if (folDbg >= 1) printf("ZZ_PREDICATE pc_%s ", predName);  
    //predicate has not been declared a function
  zzassert(zzdomain->getFunctionId(predName) < 0, 
           "not expecting pred name to be declared as a function name");
  zzassert(zzpredTemplate==NULL,"expecting zzpredTemplate==NULL");
  zzpredTemplate = new PredicateTemplate();
  zzpredTemplate->setName(predName);
  delete [] predName;
}
#line 1696 "fol.tab.c"
    break;

  case 55:
#line 559 "../src/parser/fol.y"
       { if (folDbg >= 1) printf("( "); zzconsumeToken(zztokenList,"("); }
#line 1702 "fol.tab.c"
    break;

  case 56:
#line 560 "../src/parser/fol.y"
       { if (folDbg >= 2) printf("predicate_declaration: types\n"); }
#line 1708 "fol.tab.c"
    break;

  case 57:
#line 562 "../src/parser/fol.y"
{  
  if (folDbg >= 1) printf(") "); 

  zzconsumeToken(zztokenList,")");

  zzassert(zzpredTemplate, "not expecting zzpredTemplate==NULL");
  int id = zzdomain->addPredicateTemplate(zzpredTemplate);
  zzassert(id >= 0, "expecting pred template id >= 0");
  zzpredTemplate->setId(id);
  zzpredTemplate = NULL;
}
#line 1724 "fol.tab.c"
    break;

  case 58:
#line 575 "../src/parser/fol.y"
{
  const char* predName = zztokenList.removeLast();

  if (folDbg >= 1) printf("ZZ_PREDICATE pc_%s ", predName);  
    //predicate has not been declared a function
  zzassert(zzdomain->getFunctionId(predName) < 0, 
           "not expecting pred name to be declared as a function name");
  zzassert(zzpredTemplate==NULL,"expecting zzpredTemplate==NULL");
  zzpredTemplate = new PredicateTemplate();
  zzpredTemplate->setName(predName);
  delete [] predName;

	// Declare this predicate to have type "AlchemyPropositionalType"
  const char* varName = Domain::PROPOSITIONAL_TYPE;
  if (folDbg >= 1) printf("t_%s ", varName);
  if (!zzdomain->isType(varName))
  {
    int id = zzaddTypeToDomain(zzdomain, varName);
    zzassert(id >= 0, "expecting var id >= 0");
  }
  zzaddType(varName, zzpredTemplate, NULL, false, zzdomain);

  zzassert(zzpredTemplate, "not expecting zzpredTemplate==NULL");
  int templateId = zzdomain->addPredicateTemplate(zzpredTemplate);
  zzassert(templateId >= 0, "expecting pred template id >= 0");
  zzpredTemplate->setId(templateId);
  zzpredTemplate = NULL;
}
#line 1757 "fol.tab.c"
    break;

  case 59:
#line 611 "../src/parser/fol.y"
{ 
  const char* retTypeName = zztokenList.removeLast();
  if (folDbg >= 1) printf("ZZ_FUNCTION t_%s ", retTypeName); 
  if (folDbg >= 2) printf("function_declaration: ZZ_VARIABLE\n"); 

  if (!zzdomain->isType(retTypeName))
  {
    int id = zzaddTypeToDomain(zzdomain, retTypeName);
    zzassert(id >= 0, "expecting retTypeName's id >= 0");
  }

  zzassert(zzfuncTemplate==NULL, "expecting zzfuncTemplate==NULL");
  zzfuncTemplate = new FunctionTemplate();
  zzfuncTemplate->setRetTypeName(retTypeName,zzdomain);

  // We are creating a new predicate as well
  zzassert(zzpredTemplate==NULL,"expecting zzpredTemplate==NULL");
  zzpredTemplate = new PredicateTemplate();
  zzaddType(retTypeName, zzpredTemplate, NULL, false, zzdomain);

  delete [] retTypeName;
}
#line 1784 "fol.tab.c"
    break;

  case 60:
#line 634 "../src/parser/fol.y"
{
  const char* funcName = zztokenList.removeLast();

  if (folDbg >= 1) printf("fc_%s ", funcName); 
  zzassert(zzdomain->getPredicateId(funcName) < 0, 
           "not expecting func name to be declared as pred name");
  zzfuncTemplate->setName(funcName);

  // Predicate name is PredicateTemplate::ZZ_RETURN_PREFIX + function name
  char* predName;
  predName = (char *)malloc((strlen(PredicateTemplate::ZZ_RETURN_PREFIX) +
  							strlen(funcName) + 1)*sizeof(char));
  strcpy(predName, PredicateTemplate::ZZ_RETURN_PREFIX);
  strcat(predName, funcName);
    	
  // Check that predicate has not been declared a function
  zzassert(zzdomain->getFunctionId(predName) < 0, 
           "not expecting pred name to be declared as a function name");
  zzassert(zzpredTemplate,"expecting zzpredTemplate!=NULL");
  zzpredTemplate->setName(predName);

  free(predName);
  delete [] funcName;
}
#line 1813 "fol.tab.c"
    break;

  case 61:
#line 659 "../src/parser/fol.y"
{
  zzconsumeToken(zztokenList,"(");
  if (folDbg >= 1) printf("( "); 
  if (folDbg >= 2) printf("function_declaration: types\n"); 
}
#line 1823 "fol.tab.c"
    break;

  case 62:
#line 665 "../src/parser/fol.y"
{  
  zzconsumeToken(zztokenList,")");
  if (folDbg >= 1) printf(") "); 
  zzassert(zzfuncTemplate, "expecting zzfuncTemplate != NULL");
  int id = zzdomain->addFunctionTemplate(zzfuncTemplate);
  zzassert(id >= 0, "expecting function template's id >= 0");
  zzfuncTemplate->setId(id);
  zzfuncTemplate = NULL;

  zzassert(zzpredTemplate, "not expecting zzpredTemplate==NULL");
  // Predicate could already be there
  if (!zzdomain->isPredicate(zzpredTemplate->getName()))
  {
    int predId = zzdomain->addPredicateTemplate(zzpredTemplate);
    zzassert(predId >= 0, "expecting pred template id >= 0");
    zzpredTemplate->setId(predId);
  }
  zzpredTemplate = NULL;

}
#line 1848 "fol.tab.c"
    break;

  case 65:
#line 694 "../src/parser/fol.y"
  { if (folDbg >= 1) printf(", "); zzconsumeToken(zztokenList,","); }
#line 1854 "fol.tab.c"
    break;

  case 67:
#line 698 "../src/parser/fol.y"
  { if (folDbg >= 1) printf(", "); zzconsumeToken(zztokenList,","); }
#line 1860 "fol.tab.c"
    break;

  case 71:
#line 706 "../src/parser/fol.y"
{  
  const char* ttype = zztokenList.removeLast();
  if (folDbg >= 1) printf("t_%s ", ttype);
  zzaddType(ttype, zzpredTemplate, NULL, false, zzdomain);
  // If we are in a function definition, then add the type to the function too
  if (zzfuncTemplate)
	zzaddType(ttype, NULL, zzfuncTemplate, false, zzdomain);
  delete [] ttype;
}
#line 1874 "fol.tab.c"
    break;

  case 73:
#line 718 "../src/parser/fol.y"
{
  const char* varName = zztokenList.removeLast();
  if (folDbg >= 1) printf("t_%s ", varName);
  zzassert(!zzdomain->isType(varName), "expecting varName to be not a type");
  int id = zzaddTypeToDomain(zzdomain, varName);
  zzassert(id >= 0, "expecting var id >= 0");
  zzaddType(varName, zzpredTemplate, NULL, false, zzdomain);
  // If we are in a function definition, then add the type to the function too
  if (zzfuncTemplate)
	zzaddType(varName, NULL, zzfuncTemplate, false, zzdomain);
  delete [] varName;
}
#line 1891 "fol.tab.c"
    break;

  case 75:
#line 734 "../src/parser/fol.y"
  {
  }
#line 1898 "fol.tab.c"
    break;

  case 76:
#line 737 "../src/parser/fol.y"
  {
    zzconsumeToken(zztokenList, "!");
    if (folDbg >= 1) printf("! "); 
    if (zzfuncTemplate)
      zzerr("'!' cannot be used in a function declaration.");
    zzassert(zzpredTemplate, "'!' used outside a predicate declaration.");

    int termIdx = zzpredTemplate->getNumTerms()-1;
    zzpredTemplate->addUniqueVarIndex(termIdx);
  }
#line 1913 "fol.tab.c"
    break;

  case 77:
#line 753 "../src/parser/fol.y"
  { 
    zztrueFalseUnknown = 't';
  }
#line 1921 "fol.tab.c"
    break;

  case 78:
#line 757 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"!"); 
    if (folDbg >= 1) printf("! "); 
    zztrueFalseUnknown = 'f';
  }
#line 1931 "fol.tab.c"
    break;

  case 79:
#line 763 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"?"); 
    if (folDbg >= 1) printf("? "); 
    zztrueFalseUnknown = 'u';
  }
#line 1941 "fol.tab.c"
    break;

  case 80:
#line 774 "../src/parser/fol.y"
{
  const char* predName = zztokenList.removeLast();
  if (folDbg >= 1) printf("pd_%s ", predName); 
  
  zzcreatePred(zzpred, predName);
  if (zztrueFalseUnknown == 't')      zzpred->setTruthValue(TRUE);
  else if (zztrueFalseUnknown == 'f') zzpred->setTruthValue(FALSE);
  else if (zztrueFalseUnknown == 'u') zzpred->setTruthValue(UNKNOWN);
  else { zzassert(false, "expecting t,f,u"); }

  delete [] predName;
}
#line 1958 "fol.tab.c"
    break;

  case 81:
#line 787 "../src/parser/fol.y"
{  
  zzcheckPredNumTerm(zzpred);
  int predId = zzpred->getId();
  hash_map<int,PredicateHashArray*>::iterator it;
  if ((it=zzpredIdToGndPredMap.find(predId)) == zzpredIdToGndPredMap.end())
    zzpredIdToGndPredMap[predId] = new PredicateHashArray;
  
  PredicateHashArray* pha = zzpredIdToGndPredMap[predId];
  if (pha->append(zzpred) < 0)
  {
    int a = pha->find(zzpred);
    zzassert(a >= 0, "expecting ground predicate to be found");
    string origTvStr = (*pha)[a]->getTruthValueAsStr();
    (*pha)[a]->setTruthValue(zzpred->getTruthValue());
    string newTvStr = (*pha)[a]->getTruthValueAsStr();

    if (zzwarnDuplicates)
    {
      if (origTvStr.compare(newTvStr) != 0)
      {
        ostringstream oss;
        oss << "Duplicate ground predicate "; zzpred->print(oss, zzdomain); 
        oss << " found. ";
        oss << "Changed its truthValue from " << origTvStr << " to " <<newTvStr 
            << endl;
        zzwarn(oss.str().c_str());
      }
    }
    delete zzpred;
  }
  zzpred = NULL;
}
#line 1995 "fol.tab.c"
    break;

  case 82:
#line 822 "../src/parser/fol.y"
{
  // Add the one constant for propositional case
  const char* constName = Domain::PROPOSITIONAL_CONSTANT;
  if (folDbg >= 1) printf("cg_%s ", constName);
  zzaddConstantToPredFunc(constName);
}
#line 2006 "fol.tab.c"
    break;

  case 83:
#line 830 "../src/parser/fol.y"
{ 
  zzconsumeToken(zztokenList,"("); 
  if (folDbg >= 1) printf("( "); 
  if (folDbg >= 2) printf("predicate_definition: constants_in_groundings\n");
}
#line 2016 "fol.tab.c"
    break;

  case 84:
#line 836 "../src/parser/fol.y"
{ 
  zzconsumeToken(zztokenList,")"); 
  if (folDbg >= 1) printf(")\n"); 
}
#line 2025 "fol.tab.c"
    break;

  case 85:
#line 846 "../src/parser/fol.y"
{ 
  zzconsumeToken(zztokenList,"="); 
  if (folDbg >= 1) printf("= "); 
  if (folDbg >= 2) printf("function_definition: constants_in_groundings\n");
}
#line 2035 "fol.tab.c"
    break;

  case 86:
#line 852 "../src/parser/fol.y"
{
  // Predicate name is PredicateTemplate::ZZ_RETURN_PREFIX + function name
  const char* funcName = zztokenList.removeLast();
  char* predName;
  predName = (char *)malloc((strlen(PredicateTemplate::ZZ_RETURN_PREFIX) +
  							strlen(funcName) + 1)*sizeof(char));
  strcpy(predName, PredicateTemplate::ZZ_RETURN_PREFIX);
  strcat(predName, funcName);

  if (folDbg >= 1) printf("pd_%s ", predName); 
  
  zzcreatePred(zzpred, predName);
  zzpred->setTruthValue(TRUE);

  char constName[100];
  char* constString;
  if (zztmpReturnNum)
  {
  	zzcreateAndCheckIntConstant(zztmpReturnConstant, zzfunc, zzpred, zzdomain, constName);
    if (constName == NULL)
    {
      constString = (char *)malloc((strlen(zztmpReturnConstant) + 1)*sizeof(char));
      strcpy(constString, zztmpReturnConstant);
    } else
    {
	  constString = (char *)malloc((strlen(constName) + 1)*sizeof(char));
      strcpy(constString, constName);
    }
  }
  else
  {
    constString = (char *)malloc((strlen(zztmpReturnConstant) + 1)*sizeof(char));  
  	strcpy(constString, zztmpReturnConstant);
  }

  //Add return constant parsed earlier
  zzaddConstantToPredFunc(constString);

  zztmpReturnNum = false;
  free(zztmpReturnConstant);
  delete [] funcName;
  free(predName);
  free(constString);
}
#line 2084 "fol.tab.c"
    break;

  case 87:
#line 897 "../src/parser/fol.y"
{ 
  zzconsumeToken(zztokenList,"("); 
  if (folDbg >= 1) printf("( "); 
  if (folDbg >= 2) printf("function_definition: constants_in_groundings\n");
}
#line 2094 "fol.tab.c"
    break;

  case 88:
#line 903 "../src/parser/fol.y"
{ 
  zzconsumeToken(zztokenList,")"); 
  if (folDbg >= 1) printf(")\n"); 
  
  zzcheckPredNumTerm(zzpred);
  int predId = zzpred->getId();
  hash_map<int,PredicateHashArray*>::iterator it;
  if ((it=zzpredIdToGndPredMap.find(predId)) == zzpredIdToGndPredMap.end())
    zzpredIdToGndPredMap[predId] = new PredicateHashArray;
  
  PredicateHashArray* pha = zzpredIdToGndPredMap[predId];
  if (pha->append(zzpred) < 0)
  {
    int a = pha->find(zzpred);
    zzassert(a >= 0, "expecting ground predicate to be found");
    string origTvStr = (*pha)[a]->getTruthValueAsStr();
    (*pha)[a]->setTruthValue(zzpred->getTruthValue());
    string newTvStr = (*pha)[a]->getTruthValueAsStr();

    if (zzwarnDuplicates)
    {
      if (origTvStr.compare(newTvStr) != 0)
      {
        ostringstream oss;
        oss << "Duplicate ground predicate "; zzpred->print(oss, zzdomain); 
        oss << " found. ";        
        oss << "Changed its truthValue from " << origTvStr << " to " <<newTvStr 
            << endl;
        zzwarn(oss.str().c_str());
      }
    }
    //delete zzpred;
  }

  // Insert FALSE for all other return values

  zzpred = NULL;
}
#line 2137 "fol.tab.c"
    break;

  case 89:
#line 945 "../src/parser/fol.y"
  {     
    const char* constName = zztokenList.removeLast();
    if (folDbg >= 1) printf("cg_%s ", constName);
    zzaddConstantToPredFunc(constName);
    delete [] constName;
  }
#line 2148 "fol.tab.c"
    break;

  case 90:
#line 953 "../src/parser/fol.y"
  {     
    const char* constName = zztokenList.removeLast();
    if (folDbg >= 1) printf("cg_%s ", constName);
    zzaddConstantToPredFunc(constName);
    delete [] constName;
  }
#line 2159 "fol.tab.c"
    break;

  case 92:
#line 964 "../src/parser/fol.y"
  {
    if (zzconstantMustBeDeclared)
      zzerr("Constant %s must be declared before it is used.",
            zztokenList.back());
  }
#line 2169 "fol.tab.c"
    break;

  case 93:
#line 970 "../src/parser/fol.y"
  {
    const char* intStr = zztokenList.removeLast();
    char constName[100];
    zzcreateAndCheckIntConstant(intStr, zzfunc, zzpred, zzdomain, constName);
    if (constName == NULL) zztokenList.addLast(intStr);
    else                   zztokenList.addLast(constName);
    delete [] intStr;
  }
#line 2182 "fol.tab.c"
    break;

  case 94:
#line 979 "../src/parser/fol.y"
  {
    if (zzconstantMustBeDeclared)
      zzerr("Constant %s must be declared before it is used",
            zztokenList.back());
  }
#line 2192 "fol.tab.c"
    break;

  case 95:
#line 987 "../src/parser/fol.y"
  {
    const char* tmp = zztokenList.removeLast();
	zztmpReturnConstant = (char *)malloc((strlen(tmp) + 1)*sizeof(char));
  	strcpy(zztmpReturnConstant, tmp);
  	zztmpReturnNum = false;
  	delete []tmp;
  	if (folDbg >= 1) printf("ic_%s ", zztmpReturnConstant); 
  }
#line 2205 "fol.tab.c"
    break;

  case 96:
#line 996 "../src/parser/fol.y"
  {
    if (zzconstantMustBeDeclared)
      zzerr("Constant %s must be declared before it is used.",
            zztokenList.back());
    const char* tmp = zztokenList.removeLast();
	zztmpReturnConstant = (char *)malloc((strlen(tmp) + 1)*sizeof(char));
  	strcpy(zztmpReturnConstant, tmp);
  	zztmpReturnNum = false;
  	delete []tmp;
  	if (folDbg >= 1) printf("ic_%s ", zztmpReturnConstant);
  }
#line 2221 "fol.tab.c"
    break;

  case 97:
#line 1008 "../src/parser/fol.y"
  {
  	const char* tmp = zztokenList.removeLast();
  	zztmpReturnConstant = (char *)malloc((strlen(tmp) + 1)*sizeof(char));
  	strcpy(zztmpReturnConstant, tmp);
  	zztmpReturnNum = true;
  	delete []tmp;
  	if (folDbg >= 1) printf("icnum_%s ", zztmpReturnConstant); 
  }
#line 2234 "fol.tab.c"
    break;

  case 98:
#line 1017 "../src/parser/fol.y"
  {
    if (zzconstantMustBeDeclared)
      zzerr("Constant %s must be declared before it is used",
            zztokenList.back());
    const char* tmp = zztokenList.removeLast();
	zztmpReturnConstant = (char *)malloc((strlen(tmp) + 1)*sizeof(char));
  	strcpy(zztmpReturnConstant, tmp);
  	zztmpReturnNum = false;
  	delete []tmp;
  	if (folDbg >= 1) printf("ic_%s ", zztmpReturnConstant);
  }
#line 2250 "fol.tab.c"
    break;

  case 100:
#line 1035 "../src/parser/fol.y"
  {
    const char* wt = zztokenList.removeLast();
    if (folDbg >= 1) printf("n_%f ", atof(wt));
    if (zzwt) delete zzwt;
    zzwt = new double(atof(wt));
    delete [] wt;
  }
#line 2262 "fol.tab.c"
    break;

  case 101:
#line 1049 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"("); 
    if (folDbg >= 1) printf("( "); 
    if (folDbg >= 2) printf("sentence: '(' sentence\n");
    zzformulaStr.append("(");
  }
#line 2273 "fol.tab.c"
    break;

  case 102:
#line 1057 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,")"); 
    if (folDbg >= 1) printf(") "); 
    zzformulaStr.append(")");
  }
#line 2283 "fol.tab.c"
    break;

  case 103:
#line 1063 "../src/parser/fol.y"
  { if (folDbg >= 2) printf("sentence: atomic_sentence\n"); }
#line 2289 "fol.tab.c"
    break;

  case 105:
#line 1067 "../src/parser/fol.y"
  {
    const char* imp = zztokenList.removeLast(); 
    if (folDbg >= 1) printf("=> ");
    zzformulaStr.append(" => ");
    delete [] imp;
  }
#line 2300 "fol.tab.c"
    break;

  case 106:
#line 1075 "../src/parser/fol.y"
  { zzcreateListObjFromTopTwo(zzformulaListObjs, "=>"); }
#line 2306 "fol.tab.c"
    break;

  case 107:
#line 1079 "../src/parser/fol.y"
  { 
    const char* eq = zztokenList.removeLast(); 
    if (folDbg >= 1) printf("<=> ");
    zzformulaStr.append(" <=> ");
    delete [] eq;  
  }
#line 2317 "fol.tab.c"
    break;

  case 108:
#line 1087 "../src/parser/fol.y"
  { zzcreateListObjFromTopTwo(zzformulaListObjs, "<=>"); }
#line 2323 "fol.tab.c"
    break;

  case 109:
#line 1091 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"v"); 
    if (folDbg >= 1) printf("v "); 
    zzformulaStr.append(" v ");
  }
#line 2333 "fol.tab.c"
    break;

  case 110:
#line 1098 "../src/parser/fol.y"
  { zzcreateListObjFromTopTwo(zzformulaListObjs, "v"); }
#line 2339 "fol.tab.c"
    break;

  case 111:
#line 1102 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList,"^"); 
    if (folDbg >= 1) printf("^ "); 
    zzformulaStr.append(" ^ ");
  }
#line 2349 "fol.tab.c"
    break;

  case 112:
#line 1109 "../src/parser/fol.y"
  { zzcreateListObjFromTopTwo(zzformulaListObjs, "^"); }
#line 2355 "fol.tab.c"
    break;

  case 113:
#line 1113 "../src/parser/fol.y"
  { if (folDbg >= 2) printf("sentence: quantifier\n"); }
#line 2361 "fol.tab.c"
    break;

  case 114:
#line 1115 "../src/parser/fol.y"
  { 
    if (folDbg >= 2) printf("sentence: variables\n"); 
    zzformulaListObjs.push(new ListObj);
    pair<StringToStringMap*,int> pr(new StringToStringMap,zzscopeCounter++);
    zzoldNewVarList.push_front(pr);
  }
#line 2372 "fol.tab.c"
    break;

  case 115:
#line 1121 "../src/parser/fol.y"
              { if (folDbg >= 2) printf("sentence: sentence\n"); }
#line 2378 "fol.tab.c"
    break;

  case 116:
#line 1123 "../src/parser/fol.y"
  { 
    zzcreateListObjFromTopThree(zzformulaListObjs);
    pair<StringToStringMap*, int> pr = zzoldNewVarList.front();
    zzoldNewVarList.pop_front();
    delete pr.first;
  }
#line 2389 "fol.tab.c"
    break;

  case 117:
#line 1132 "../src/parser/fol.y"
  { 
    zzassert(!zzisNegated,"expecting !zzisNegated");
    zzisNegated = true;

    zzconsumeToken(zztokenList,"!");
    if (folDbg >= 1) printf("! "); 
    if (folDbg >= 2) printf("sentence: sentence\n");
    zzformulaStr.append("!");
  }
#line 2403 "fol.tab.c"
    break;

  case 118:
#line 1142 "../src/parser/fol.y"
  { zzcreateListObjFromTop(zzformulaListObjs, "!"); }
#line 2409 "fol.tab.c"
    break;

  case 119:
#line 1148 "../src/parser/fol.y"
  { 
    const char* fa = zztokenList.removeLast();
    if (folDbg >= 1) printf("FORALL ");
    zzformulaListObjs.push(new ListObj("FORALL"));
    zzformulaStr.append("FORALL ");
    delete [] fa;
  }
#line 2421 "fol.tab.c"
    break;

  case 120:
#line 1156 "../src/parser/fol.y"
  { 
    const char* ex = zztokenList.removeLast();
    if (folDbg >= 1) printf("EXIST "); 
    zzformulaListObjs.push(new ListObj("EXIST"));
    zzformulaStr.append("EXIST ");
    delete [] ex;
  }
#line 2433 "fol.tab.c"
    break;

  case 121:
#line 1168 "../src/parser/fol.y"
  { if (folDbg >= 2) printf("variables: variables\n"); }
#line 2439 "fol.tab.c"
    break;

  case 122:
#line 1170 "../src/parser/fol.y"
  {  
    zzconsumeToken(zztokenList,",");
    if (folDbg >= 1) printf(", "); 
    zzformulaStr.append(",");
  }
#line 2449 "fol.tab.c"
    break;

  case 124:
#line 1177 "../src/parser/fol.y"
                  { zzformulaStr.append(" "); }
#line 2455 "fol.tab.c"
    break;

  case 125:
#line 1182 "../src/parser/fol.y"
{
  const char* varName = zztokenList.removeLast();  
  if (folDbg >= 1) printf("v_%s ", varName); 

  //if (isupper(varName[0])) 
  if (zzisConstant(varName)) 
  {
    zzerr("Variable %s must be begin with a lowercase character.", varName);
    ((char*)varName)[0] = tolower(varName[0]);
  }

  int scopeNum = zzoldNewVarList.front().second;
  string newVarName = zzappend(varName,scopeNum);

  StringToStringMap* oldNewVarMap = zzoldNewVarList.front().first;
  (*oldNewVarMap)[varName]=newVarName;
  zzvarNameToIdMap[newVarName] = ZZVarIdType(--zzvarCounter, zzanyTypeId);
  zzformulaListObjs.top()->append(newVarName.c_str());
  zzformulaStr.append(varName); //use the old var name in the orig string
  delete [] varName;
}
#line 2481 "fol.tab.c"
    break;

  case 126:
#line 1208 "../src/parser/fol.y"
  {
    const char* predName = zztokenList.removeLast();
    if (folDbg >= 1) printf("p_%s ", predName); 

    zzfdnumPreds++;
    ListObj* predlo = new ListObj;

	if (PredicateTemplate::isInternalPredicateTemplateName(predName))
	{
	  //zzinfixPredName is misused here to store internal pred. name
	  zzinfixPredName = (char *)malloc((strlen(predName)
    								  	+ 1)*sizeof(char));
	  strcpy(zzinfixPredName, predName);
	  const PredicateTemplate* t = zzdomain->getEmptyPredicateTemplate();
      zzassert(zzpred == NULL,"expecting zzpred==NULL");
      zzpred = new Predicate(t);
      predlo->append(PredicateTemplate::EMPTY_NAME);
	}
	else
	{
      zzcreatePred(zzpred, predName);
      predlo->append(predName);
	}
	
    zzformulaStr.append(predName);
    if(zzisNegated)  { zzpred->setSense(false); zzisNegated = false; }
    zzpredFuncListObjs.push(predlo);
    delete [] predName;
  }
#line 2515 "fol.tab.c"
    break;

  case 128:
#line 1240 "../src/parser/fol.y"
  {
    ++zzfdnumPreds;
    //zzfdisEqualPred = true;
    //const PredicateTemplate* t = zzdomain->getEqualPredicateTemplate();
    const PredicateTemplate* t = zzdomain->getEmptyPredicateTemplate();

    zzassert(zzpred == NULL, "expecting zzpred==NULL");
    zzpred = new Predicate(t);

    ListObj* predlo = new ListObj;
    //predlo->append(PredicateTemplate::EQUAL_NAME);
    predlo->append(PredicateTemplate::EMPTY_NAME);
    zzpredFuncListObjs.push(predlo);
    if (zzisNegated)  { zzpred->setSense(false); zzisNegated = false; }

    if (folDbg >= 2) printf("atomic_sentence (left): term\n"); 
  }
#line 2537 "fol.tab.c"
    break;

  case 129:
#line 1259 "../src/parser/fol.y"
  {
  	ListObj* predlo = zzpredFuncListObjs.top();
    predlo->replace(PredicateTemplate::EMPTY_NAME, zzinfixPredName);
    
  	  // If type known from LHS, then set the pred types accordingly
    int lTypeId = zzgetTypeId(zzpred->getTerm(0), (*predlo)[1]->getStr());
    if (lTypeId > 0)
    {
      if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
      {
        zzsetEqPredTypeName(lTypeId);
      }
      else
 	  {
 	    zzsetInternalPredTypeName(zzinfixPredName, lTypeId);
 	  }
    }
  }
#line 2560 "fol.tab.c"
    break;

  case 130:
#line 1278 "../src/parser/fol.y"
  {  
    ListObj* predlo = zzpredFuncListObjs.top();
    //predlo->replace(PredicateTemplate::EMPTY_NAME, zzinfixPredName);

	// types are possibly unknown
	// If '=' predicate then types are possibly unknown
	//if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0) {
      int lTypeId = zzgetTypeId(zzpred->getTerm(0), (*predlo)[1]->getStr());
      int rTypeId = zzgetTypeId(zzpred->getTerm(1), (*predlo)[2]->getStr());

      if (lTypeId > 0 && rTypeId > 0) //if both types are known
      {
        if (lTypeId != rTypeId)
          zzerr("The types on the left and right of '=' must match.");
        if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
        {
 	      zzsetEqPredTypeName(lTypeId);
 	    }
 	    else
 	    {
 	      zzsetInternalPredTypeName(zzinfixPredName, lTypeId);
 	    }
      }
      else  // if only one type is known
      if ( (lTypeId<=0 && rTypeId>0) || (lTypeId>0 && rTypeId<=0) )
      {
        int knownTypeId = (lTypeId>0) ? lTypeId : rTypeId;
        if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
        {
          zzsetEqPredTypeName(knownTypeId);
        }
        else
 	    {
 	      zzsetInternalPredTypeName(zzinfixPredName, knownTypeId);
 	    }
        const char* lvarName = (*predlo)[1]->getStr();
        const char* rvarName = (*predlo)[2]->getStr();
        const char* unknownVarName = (lTypeId>0) ?  rvarName : lvarName;
        zzvarNameToIdMap[unknownVarName].typeId_ = knownTypeId;
      }
      else // if both types are unknown
      {
          //both sides must be variables
        const char* lvarName = (*predlo)[1]->getStr();
        const char* rvarName = (*predlo)[2]->getStr();
        lTypeId = zzgetVarTypeId(lvarName);
        rTypeId = zzgetVarTypeId(rvarName);
	
        if (lTypeId > 0 && rTypeId > 0) //if both types are known
        {
          if (lTypeId != rTypeId)
            zzerr("The types of %s and %s on the left and right of "
                   "'=' must match.", lvarName, rvarName);
          if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
          {
          	zzsetEqPredTypeName(lTypeId);
          }
          else
 	      {
 	      	zzsetInternalPredTypeName(zzinfixPredName, lTypeId);
 	      }
        }
        else  // if only one type is known
        if ( (lTypeId <= 0 && rTypeId > 0) || (lTypeId > 0 && rTypeId <= 0) )
        {
          int knownTypeId = (lTypeId > 0) ? lTypeId : rTypeId;
          if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME) == 0)
          {
          	zzsetEqPredTypeName(knownTypeId);
          }
          else
 	      {
 	      	zzsetInternalPredTypeName(zzinfixPredName, knownTypeId);
 	      }
          const char* unknowVarName = (lTypeId>0) ?  rvarName : lvarName;
          zzvarNameToIdMap[unknowVarName].typeId_ = knownTypeId;
        }
        else
        {      
		  if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
          {
          	string unknownEqName = zzappend(PredicateTemplate::EQUAL_NAME, 
            	                            zzeqTypeCounter++);
          	zzeqPredList.push_back(ZZUnknownEqPredInfo(unknownEqName,lvarName,
                                                       rvarName));
          	predlo->replace(PredicateTemplate::EQUAL_NAME, unknownEqName.c_str());
          }
          else
          {
          	string unknownIntPredName =
          	  zzappendWithUnderscore(zzinfixPredName, zzintPredTypeCounter++);
          	zzintPredList.push_back(ZZUnknownIntPredInfo(unknownIntPredName, lvarName,
                                                       	 rvarName));
          	predlo->replace(zzinfixPredName, unknownIntPredName.c_str());
          }
        }
      }
	//}
	//else // Infix predicate other than '='
	//{
	  //Only left term could be unknown
	  //const char* leftTerm = (*predlo)[1]->getStr();
	//}

    zzassert(zzpredFuncListObjs.size()==1,
             "expecting zzpredFuncListObjs.size()==1");
    ListObj* topPredlo = zzpredFuncListObjs.top();
    zzpredFuncListObjs.pop();
    zzformulaListObjs.push(topPredlo);
      // This allows for the '!=' operator
    if (zzisNegated)
    {
      zzcreateListObjFromTop(zzformulaListObjs, "!");
      zzisNegated = false;
    }
    
	delete zzpred;
	zzpred = NULL;
	
	// If we have replaced a function inside the predicate
	// then we have to add the conjunction
	while (!zzfuncConjStack.empty())
	{
	  // create the second part of the conjunction
	  //zzformulaStr.append(" ^ ");
		
      ListObj* topPredlo = zzfuncConjStack.top();
	  zzfuncConjStack.pop();
      //zzformulaListObjs.push(topPredlo);
	  //zzcreateListObjFromTopTwo(zzformulaListObjs, "^");
	  zzformulaListObjs.push(topPredlo);
	  zzcreateListObjFromTopTwo(zzformulaListObjs, "v");
	} //while (!zzfuncConjStack.empty())

	if (!zzfuncConjStr.empty())
	{
	  zzformulaStr.append(zzfuncConjStr);
	  zzfuncConjStr.clear();
	}
	zzfunc = NULL;
	free(zzinfixPredName);
    zzinfixPredName = NULL;
  }
#line 2708 "fol.tab.c"
    break;

  case 131:
#line 1425 "../src/parser/fol.y"
  {
	// Add the one constant for propositional case
    const char* constName = Domain::PROPOSITIONAL_CONSTANT;
    if (folDbg >= 1) printf("c2_%s ", constName); 
    zztermIsConstant(constName, constName, false);

    zzcheckPredNumTerm(zzpred);
    delete zzpred;
    zzpred = NULL;
    zzassert(zzpredFuncListObjs.size()==1,
             "expecting zzpredFuncListObjs.size()==1");
    ListObj* predlo = zzpredFuncListObjs.top();
    zzpredFuncListObjs.pop();
    zzformulaListObjs.push(predlo);
  }
#line 2728 "fol.tab.c"
    break;

  case 132:
#line 1442 "../src/parser/fol.y"
  {  
    zzconsumeToken(zztokenList, "(");
    if (folDbg >= 1) printf("( "); 
    if (folDbg >= 2) printf("atomic_sentence: terms\n"); 
    zzformulaStr.append("(");
  }
#line 2739 "fol.tab.c"
    break;

  case 133:
#line 1450 "../src/parser/fol.y"
  {  
    zzconsumeToken(zztokenList, ")");
    if (folDbg >= 1) printf(") "); 

	  //If an internal pred., then need to determine type
	  //zzinfixPredName is misused here to store internal pred. name
	if (zzinfixPredName)
	{
	  ListObj* predlo = zzpredFuncListObjs.top();
      predlo->replace(PredicateTemplate::EMPTY_NAME, zzinfixPredName);
		// types are possibly unknown
		// If '=' predicate then types are possibly unknown
		//if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0) {
      int lTypeId = zzgetTypeId(zzpred->getTerm(0), (*predlo)[1]->getStr());
      int rTypeId = zzgetTypeId(zzpred->getTerm(1), (*predlo)[2]->getStr());

      if (lTypeId > 0 && rTypeId > 0) //if both types are known
      {
        if (lTypeId != rTypeId)
          zzerr("The types on the left and right of '=' must match.");
        if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
        {
 	      zzsetEqPredTypeName(lTypeId);
 	    }
 	    else
 	    {
 	      zzsetInternalPredTypeName(zzinfixPredName, lTypeId);
 	    }
      }
      else  // if only one type is known
      if ( (lTypeId<=0 && rTypeId>0) || (lTypeId>0 && rTypeId<=0) )
      {
        int knownTypeId = (lTypeId>0) ? lTypeId : rTypeId;
        if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
        {
          zzsetEqPredTypeName(knownTypeId);
        }
        else
 	    {
 	      zzsetInternalPredTypeName(zzinfixPredName, knownTypeId);
 	    }
        const char* lvarName = (*predlo)[1]->getStr();
        const char* rvarName = (*predlo)[2]->getStr();
        const char* unknownVarName = (lTypeId>0) ?  rvarName : lvarName;
        zzvarNameToIdMap[unknownVarName].typeId_ = knownTypeId;
      }
      else // if both types are unknown
      {
          //both sides must be variables
        const char* lvarName = (*predlo)[1]->getStr();
        const char* rvarName = (*predlo)[2]->getStr();
        lTypeId = zzgetVarTypeId(lvarName);
        rTypeId = zzgetVarTypeId(rvarName);
	
        if (lTypeId > 0 && rTypeId > 0) //if both types are known
        {
          if (lTypeId != rTypeId)
            zzerr("The types of %s and %s on the left and right of "
                   "'=' must match.", lvarName, rvarName);
          if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
          {
          	zzsetEqPredTypeName(lTypeId);
          }
          else
 	      {
 	      	zzsetInternalPredTypeName(zzinfixPredName, lTypeId);
 	      }
        }
        else  // if only one type is known
        if ( (lTypeId<=0 && rTypeId>0) || (lTypeId>0 && rTypeId<=0) )
        {
          int knownTypeId = (lTypeId>0) ? lTypeId : rTypeId;
          if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
          {
          	zzsetEqPredTypeName(knownTypeId);
          }
          else
 	      {
 	      	zzsetInternalPredTypeName(zzinfixPredName, knownTypeId);
 	      }
          const char* unknowVarName = (lTypeId>0) ?  rvarName : lvarName;
          zzvarNameToIdMap[unknowVarName].typeId_ = knownTypeId;
        }
        else
        {      
		  if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
          {
          	string unknownEqName = zzappend(PredicateTemplate::EQUAL_NAME, 
            	                            zzeqTypeCounter++);
          	zzeqPredList.push_back(ZZUnknownEqPredInfo(unknownEqName,lvarName,
                                                       rvarName));
          	predlo->replace(PredicateTemplate::EQUAL_NAME, unknownEqName.c_str());
          }
          else
          {
          	string unknownIntPredName =
          	  zzappendWithUnderscore(zzinfixPredName, zzintPredTypeCounter++);
          	zzintPredList.push_back(ZZUnknownIntPredInfo(unknownIntPredName, lvarName,
                                                       	 rvarName));
          	predlo->replace(zzinfixPredName, unknownIntPredName.c_str());
          }
        }
      }
	  free(zzinfixPredName);
      zzinfixPredName = NULL;
	}

    zzcheckPredNumTerm(zzpred);
    delete zzpred;
    zzpred = NULL;
    zzassert(zzpredFuncListObjs.size()==1,
             "expecting zzpredFuncListObjs.size()==1");
    ListObj* predlo = zzpredFuncListObjs.top();
    zzpredFuncListObjs.pop();

    if (zzisAsterisk)
    {
      zzisAsterisk = false;
      ListObj* lo = new ListObj;
      lo->append("*"); lo->append(predlo);
      zzformulaListObjs.push(lo);
    }
    else
      zzformulaListObjs.push(predlo);

    zzformulaStr.append(")");

	// If we have replaced a function inside the predicate
	// then we have to add the conjunction
	while (!zzfuncConjStack.empty())
	{
		// create the second part of the conjunction
		//zzformulaStr.append(" ^ ");
      ListObj* topPredlo = zzfuncConjStack.top();
      zzfuncConjStack.pop();
      //zzformulaListObjs.push(topPredlo);
      //zzcreateListObjFromTopTwo(zzformulaListObjs, "^");
      zzformulaListObjs.push(topPredlo);
      zzcreateListObjFromTopTwo(zzformulaListObjs, "v");
	} //while (!zzfuncConjStack.empty())

	if (!zzfuncConjStr.empty())
	{
      zzformulaStr.append(zzfuncConjStr);
      zzfuncConjStr.clear();
	}
	zzfunc = NULL;
  }
#line 2892 "fol.tab.c"
    break;

  case 134:
#line 1602 "../src/parser/fol.y"
  {
  	zzconsumeToken(zztokenList, ">");
    if (folDbg >= 1) printf("> "); 
    if (folDbg >= 2) printf("atomic_sentence (right): term\n"); 
    zzformulaStr.append(" > ");
    zzinfixPredName = (char *)malloc((strlen(PredicateTemplate::GT_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixPredName, PredicateTemplate::GT_NAME);
  	//zzcreateInternalPredTemplate(zzinfixPredName);
    //const PredicateTemplate* t = zzdomain->getPredicateTemplate(zzinfixPredName);
	//zzpred->setTemplate((PredicateTemplate*)t);
  }
#line 2909 "fol.tab.c"
    break;

  case 135:
#line 1616 "../src/parser/fol.y"
  {
   	zzconsumeToken(zztokenList, "<");
    if (folDbg >= 1) printf("< "); 
    if (folDbg >= 2) printf("atomic_sentence (right): term\n"); 
    zzformulaStr.append(" < "); 
    zzinfixPredName = (char *)malloc((strlen(PredicateTemplate::LT_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixPredName, PredicateTemplate::LT_NAME);
  	//zzcreateInternalPredTemplate(zzinfixPredName);
    //const PredicateTemplate* t = zzdomain->getPredicateTemplate(zzinfixPredName);
	//zzpred->setTemplate((PredicateTemplate*)t);
  }
#line 2926 "fol.tab.c"
    break;

  case 136:
#line 1630 "../src/parser/fol.y"
  {
  	zzconsumeToken(zztokenList, ">");
    if (folDbg >= 1) printf(">");
    zzformulaStr.append(" >");
    zzconsumeToken(zztokenList, "=");
    if (folDbg >= 1) printf("= "); 
    if (folDbg >= 2) printf("atomic_sentence (right): term\n"); 
    zzformulaStr.append("= ");
    zzinfixPredName = (char *)malloc((strlen(PredicateTemplate::GTEQ_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixPredName, PredicateTemplate::GTEQ_NAME);
  	//zzcreateInternalPredTemplate(zzinfixPredName);
	//const PredicateTemplate* t = zzdomain->getPredicateTemplate(zzinfixPredName);
	//zzpred->setTemplate((PredicateTemplate*)t);
  }
#line 2946 "fol.tab.c"
    break;

  case 137:
#line 1647 "../src/parser/fol.y"
  {
	zzconsumeToken(zztokenList, "<");
    if (folDbg >= 1) printf("<");
    zzformulaStr.append(" <");
    zzconsumeToken(zztokenList, "=");
    if (folDbg >= 1) printf("= "); 
    if (folDbg >= 2) printf("atomic_sentence (right): term\n"); 
    zzformulaStr.append("= ");
    zzinfixPredName = (char *)malloc((strlen(PredicateTemplate::LTEQ_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixPredName, PredicateTemplate::LTEQ_NAME);
  	//zzcreateInternalPredTemplate(zzinfixPredName);
    //const PredicateTemplate* t = zzdomain->getPredicateTemplate(zzinfixPredName);
	//zzpred->setTemplate((PredicateTemplate*)t);
  }
#line 2966 "fol.tab.c"
    break;

  case 138:
#line 1664 "../src/parser/fol.y"
  {
  	zzconsumeToken(zztokenList, "=");
    if (folDbg >= 1) printf("= "); 
    if (folDbg >= 2) printf("atomic_sentence (right): term\n"); 
    zzformulaStr.append(" = ");
    zzinfixPredName = (char *)malloc((strlen(PredicateTemplate::EQUAL_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixPredName, PredicateTemplate::EQUAL_NAME);
    const PredicateTemplate* t = zzdomain->getEqualPredicateTemplate();
	zzpred->setTemplate((PredicateTemplate*)t);
  }
#line 2982 "fol.tab.c"
    break;

  case 139:
#line 1677 "../src/parser/fol.y"
  {
  	zzconsumeToken(zztokenList, "!");
  	zzconsumeToken(zztokenList, "=");
    if (folDbg >= 1) printf("!= "); 
    if (folDbg >= 2) printf("atomic_sentence (right): term\n"); 
    zzformulaStr.append(" != ");
    zzinfixPredName = (char *)malloc((strlen(PredicateTemplate::EQUAL_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixPredName, PredicateTemplate::EQUAL_NAME);
    const PredicateTemplate* t = zzdomain->getEqualPredicateTemplate();
	zzpred->setTemplate((PredicateTemplate*)t);
	  // Theoretically, we could have "!(a1 != a2)" which would be "a1 = a2"
    if (zzpred->getSense())
    {
      zzpred->setSense(false);
      zzisNegated = true;
    }
    else { zzpred->setSense(true); }
  }
#line 3006 "fol.tab.c"
    break;

  case 141:
#line 1702 "../src/parser/fol.y"
  { 
    zzconsumeToken(zztokenList, "*");
    if (folDbg >= 1) printf("* "); 
    if (zzisNegated) zzerr("'!' and '*' cannot be used at the same time");
    zznumAsterisk++;
    zzassert(!zzisAsterisk,"expecting !zzisAsterisk");
    zzisAsterisk = true;
    zzformulaStr.append("*");
  }
#line 3020 "fol.tab.c"
    break;

  case 142:
#line 1718 "../src/parser/fol.y"
  {  
    zzconsumeToken(zztokenList, ",");
    if (folDbg >= 1) printf(", "); 
    if (folDbg >= 2) printf("terms: term\n"); 
    // While parsing function, we do not want to append anything to the formula
    if (zzfunc == NULL) zzformulaStr.append(",");
  }
#line 3032 "fol.tab.c"
    break;

  case 144:
#line 1728 "../src/parser/fol.y"
  {
  	// After the first term in an internal pred., check if we can determine type
  	if (zzpred && zzpred->isEmptyPred() &&
  		zzpred->getNumTerms() == 1 && zzinfixPredName)
  	{
      ListObj* predlo = zzpredFuncListObjs.top();
      predlo->replace(PredicateTemplate::EMPTY_NAME, zzinfixPredName);
    
  	  	// If type known from term, then set the pred types accordingly
	  int lTypeId = zzgetTypeId(zzpred->getTerm(0), (*predlo)[1]->getStr());
      if (lTypeId>0)
      {
      	if (strcmp(zzinfixPredName, PredicateTemplate::EQUAL_NAME)==0)
      	{
          zzsetEqPredTypeName(lTypeId);
      	}
      	else
 	  	{
 	      zzsetInternalPredTypeName(zzinfixPredName, lTypeId);
 	  	}
      }
  	}
  }
#line 3060 "fol.tab.c"
    break;

  case 145:
#line 1756 "../src/parser/fol.y"
  {
    const char* constName = zztokenList.removeLast();
    if (folDbg >= 1) printf("c2_%s ", constName); 
    zztermIsConstant(constName, constName, true);
    if (zzfunc) zzfdfuncConstants.append(string(constName));
    else        zzfdconstName = constName;
    delete [] constName;
  }
#line 3073 "fol.tab.c"
    break;

  case 146:
#line 1766 "../src/parser/fol.y"
  {
    const char* constName = zztokenList.removeLast();
    if (folDbg >= 1) printf("c2_%s ", constName); 
      if (zzconstantMustBeDeclared)
        zzerr("Constant %s must be declared before it is used", constName);
    zztermIsConstant(constName, constName, true);
    if (zzfunc) zzfdfuncConstants.append(string(constName));
    else        zzfdconstName = constName;
    delete [] constName;
  }
#line 3088 "fol.tab.c"
    break;

  case 147:
#line 1778 "../src/parser/fol.y"
  {
    const char* intStr = zztokenList.removeLast();
    if (folDbg >= 1) printf("c3_%s ", intStr);

    char constName[100];
    zzcreateAndCheckIntConstant(intStr, zzfunc, zzpred, zzdomain, constName);
    if (constName == NULL) { break; delete [] intStr; }

    zztermIsConstant(constName, intStr, true);
    if (zzfunc) zzfdfuncConstants.append(string(constName));
    else        zzfdconstName = constName;
    delete [] intStr;
  }
#line 3106 "fol.tab.c"
    break;

  case 148:
#line 1793 "../src/parser/fol.y"
  {
    zztermIsVariable(folDbg);
    if (zzisPlus) zzisPlus = false;
  }
#line 3115 "fol.tab.c"
    break;

  case 149:
#line 1799 "../src/parser/fol.y"
  {
    zzconsumeToken(zztokenList, "+");
    if (folDbg >= 1) printf("+ "); 
    zzassert(!zzisPlus,"expecting !zzisPlus");
    zzisPlus = true;
    zzformulaStr.append("+");
    zztermIsVariable(folDbg);
    if (zzisPlus) zzisPlus = false;
  }
#line 3129 "fol.tab.c"
    break;

  case 150:
#line 1810 "../src/parser/fol.y"
  {
    zzassert(zzfunc != NULL,"expecting zzfunc != NULL");
    zzcheckFuncNumTerm(zzfunc);
    zzassert(zzpred != NULL, "expecting zzpred != NULL");

      // replace function
	 
	  // Append Term funcVar<zzfuncVarCounter> to predicate where
      // function appears and set flag to add conjunction

      // 1. Make new variable
    char* varName;
    string newVarName;
    
      // Check if function mapping already occurs in formula
    ZZFuncToFuncVarMap::iterator mit;
    if ((mit = zzfuncToFuncVarMap.find(zzfunc)) != zzfuncToFuncVarMap.end())
    {
      newVarName = (*mit).second;
      varName = (char *)malloc((strlen(newVarName.c_str()) + 1) * sizeof(char));
      strcpy(varName, newVarName.c_str());
    }
    else
    {
      char funcVarCounterString[10];
      int funcVarCounterLength =
        sprintf(funcVarCounterString, "%d", zzfuncVarCounter);
      varName = (char *)malloc((strlen(ZZ_FUNCVAR_PREFIX) +
  								funcVarCounterLength + 1)*sizeof(char));
      strcpy(varName, ZZ_FUNCVAR_PREFIX);
      strcat(varName, funcVarCounterString);
      ++zzfdnumVars;
      ++zzfuncVarCounter;
      newVarName = zzgetNewVarName(varName);
      
      Function* func = new Function(*zzfunc);
      zzfuncToFuncVarMap[func] = newVarName;
    }

   	bool rightNumTerms = true;
   	bool rightType = true;
   	int exp, unexp;

      // 2. Create new predicate
      // Predicate name is PredicateTemplate::ZZ_RETURN_PREFIX + function name
	char* predName;
	predName = (char *)malloc((strlen(PredicateTemplate::ZZ_RETURN_PREFIX) +
  	    					   strlen(zzfunc->getName()) + 1)*sizeof(char));
	strcpy(predName, PredicateTemplate::ZZ_RETURN_PREFIX);
 	strcat(predName, zzfunc->getName());
    	
	// Only insert predicate declaration, if not yet declared
	if (zzdomain->getPredicateId(predName) < 0)
	{
      zzassert(zzpredTemplate==NULL,"expecting zzpredTemplate==NULL");
      zzpredTemplate = new PredicateTemplate();
      zzpredTemplate->setName(predName);
			
      // Register the types
      // First parameter is the return type
	  const char* ttype = zzfunc->getRetTypeName();
	  zzaddType(ttype, zzpredTemplate, NULL, false, zzdomain);

	  // Register the parameter types
	  for (int i = 0; i < zzfunc->getNumTerms(); i++)
	  {
		const char* ttype = zzfunc->getTermTypeAsStr(i);
		zzaddType(ttype, zzpredTemplate, NULL, false, zzdomain);
	  }
	
	  zzassert(zzpredTemplate, "not expecting zzpredTemplate==NULL");
	  int id = zzdomain->addPredicateTemplate(zzpredTemplate);
	  zzassert(id >= 0, "expecting pred template id >= 0");
	  zzpredTemplate->setId(id);
	  zzpredTemplate = NULL;
	}

	Predicate* prevPred = zzpred;
	zzpred = NULL;
    zzfdnumPreds++;
	zzcreatePred(zzpred, predName);
    
    ListObj* predlo = new ListObj;
    predlo->append(predName);
		
	// Put predicate list object in stack to be used in conjunction later
    zzfuncConjStack.push(predlo);
    //zzfuncConjStr.append(" ^ ");
    zzfuncConjStr.append(" v !");
    zzfuncConjStr.append(predName);
	zzfuncConjStr.append("(");
    zzputVariableInPred(varName, folDbg);
    zzfuncConjStack.top()->append(varName);
    zzfuncConjStr.append(varName);
      	
	// Information about the terms is in zzfunc
	for (int i = 0; i < zzfunc->getNumTerms(); i++)
	{
	  zzfuncConjStr.append(", ");
	  Term* term = new Term(*zzfunc->getTerm(i));
	  zzpred->appendTerm(term);

	  const char* name;
	  if (term->getType() == Term::VARIABLE)
	  {
		name = (*zzpredFuncListObjs.top())[i+1]->getStr();
	  }
	  else if (term->getType() == Term::CONSTANT)
	  {
		name = zzdomain->getConstantName(term->getId());
	  }
	  zzpredFuncListObjs.top()->append(name);
	  zzfuncConjStack.top()->append(name);
	  zzfuncConjStr.append(name);
	}
	zzfuncConjStr.append(")");
    zzcreateListObjFromTop(zzfuncConjStack, "!");
    
    // 4. Append new variable to function in stack or to predicate
    if (!zzfuncStack.empty())
    {
   	  Function* prevFunc = zzfuncStack.top(); 
	  zzfuncStack.pop();
    
      // check that we have not exceeded the number of terms
      if ((unexp = prevFunc->getNumTerms()) ==
       	  (exp = prevFunc->getTemplate()->getNumTerms()))
      {
       	rightNumTerms = false;
       	zzerr("Wrong number of terms for function %s. "
           	  "Expected %d but given %d", prevFunc->getName(), exp, unexp+1);
      }
      
      int varId = -1;      
      if (rightNumTerms)
      {
       	// check that the variable is of the right type
     	int typeId = prevFunc->getTermTypeAsInt(prevFunc->getNumTerms());
      	rightType = zzcheckRightTypeAndGetVarId(typeId, newVarName.c_str(),
	                                            varId);
      }

      if (rightNumTerms && rightType)
      {
     	prevFunc->appendTerm(new Term(varId, (void*)prevFunc, false));
     	zzpredFuncListObjs.pop();
    	zzpredFuncListObjs.top()->append(newVarName.c_str());
      }
    	      	  
      zzfunc = prevFunc;
    }
	else // function stack is empty, so append to predicate
    {
      // check that we have not exceeded the number of terms
      if ((unexp = prevPred->getNumTerms()) ==
      	  (exp = prevPred->getTemplate()->getNumTerms()))
      {
        rightNumTerms = false;
        zzerr("Wrong number of terms for predicate %s. "
              "Expected %d but given %d", prevPred->getName(), exp, unexp+1);
      }
        
      int varId = -1;
      if (rightNumTerms)
      {
          // check that the variable is of the right type
        int typeId = prevPred->getTermTypeAsInt(prevPred->getNumTerms());
        rightType = zzcheckRightTypeAndGetVarId(typeId, newVarName.c_str(),
        									    varId);
      }
      
	  if (rightNumTerms && rightType)
	  {
		prevPred->appendTerm(new Term(varId, (void*)prevPred, true));

   		// Pop the function from the stack
   		zzoldFuncLo = zzpredFuncListObjs.top();
   		zzpredFuncListObjs.pop();
   		zzpredFuncListObjs.top()->append(newVarName.c_str());
   		zzformulaStr.append(varName);
      }
	  zzfunc = NULL;
        	
    }
    free(varName);
	free(predName);
	//zzformulaStr.append(")");

    delete zzpred;
	zzpred = prevPred;
  }
#line 3325 "fol.tab.c"
    break;

  case 151:
#line 2006 "../src/parser/fol.y"
  {
    const char* funcName = zztokenList.removeLast();
    if (folDbg >= 1) printf("f_%s ", funcName);
    if (zzfunc != NULL) { zzfuncStack.push(zzfunc); zzfunc = NULL; }
    ++zzfdnumFuncs;
    zzfdfuncName = funcName;

    ListObj* funclo = new ListObj;

	  // Check if internal function
 	if (FunctionTemplate::isInternalFunctionTemplateName(funcName))
	{
	  zzinfixFuncName = (char *)malloc((strlen(funcName)
    								  	+ 1)*sizeof(char));
	  strcpy(zzinfixFuncName, funcName);
	  const FunctionTemplate* t;
	  if (FunctionTemplate::isInternalFunctionUnaryTemplateName(funcName))
	  	t = zzdomain->getEmptyFunctionUnaryTemplate();
	  else
	  	t = zzdomain->getEmptyFunctionBinaryTemplate();
      zzassert(zzfunc == NULL,"expecting zzfunc==NULL");
      zzfunc = new Function(t);
      funclo->append(FunctionTemplate::EMPTY_FTEMPLATE_NAME);
	}
	else
	{
	  zzcreateFunc(zzfunc, funcName); 
	  funclo->append(funcName);
	}
	
    zzpredFuncListObjs.push(funclo);
    //zzformulaStr.append(funcName);

    delete [] funcName;
  }
#line 3365 "fol.tab.c"
    break;

  case 152:
#line 2042 "../src/parser/fol.y"
  {
    zzconsumeToken(zztokenList, "(");
    if (folDbg >= 1) printf("( "); 
    if (folDbg >= 2) printf("term: terms\n");
  }
#line 3375 "fol.tab.c"
    break;

  case 153:
#line 2048 "../src/parser/fol.y"
  {
  	  //If an internal func., then need to determine type
	if (zzinfixFuncName)
	{
	  ListObj* funclo = zzpredFuncListObjs.top();
      funclo->replace(FunctionTemplate::EMPTY_FTEMPLATE_NAME, zzinfixFuncName);
	  const FunctionTemplate* t =
	    zzgetGenericInternalFunctionTemplate(zzinfixFuncName);
		// If in a pred. (not LHS of infix pred.), then we know the return type
	  if (zzpred)
	  {
	  	((FunctionTemplate*)t)->setRetTypeId(
	  		zzpred->getTermTypeAsInt(zzpred->getNumTerms()), zzdomain);
      }
	  zzfunc->setTemplate((FunctionTemplate*)t);

		// types are possibly unknown
	  bool unknownTypes = false;
		
		// First element is return type
	  Array<int> typeIds(zzfunc->getNumTerms() + 1);
	  typeIds.append(zzfunc->getRetTypeId());
	  if (typeIds[0] <= 0) unknownTypes = true;
		
		// Then term types
	  for (int i = 1; i <= zzfunc->getNumTerms(); i++)
	  {
	  	typeIds.append(zzgetTypeId(zzfunc->getTerm(i-1), (*funclo)[i]->getStr()));
	  	if (typeIds[i] <= 0) unknownTypes = true;
	  }

		// If all types are known
	  if (!unknownTypes)
	  {
 	  	zzsetInternalFuncTypeName(zzinfixFuncName, typeIds);
	  }
      else // Not all types are known, delay processing
      {
      	Array<string> varNames(typeIds.size());
      	
      	char* varName;
    	char funcVarCounterString[10];
    	int funcVarCounterLength =
      		sprintf(funcVarCounterString, "%d", zzfuncVarCounter);
    	varName = (char *)malloc((strlen(ZZ_FUNCVAR_PREFIX) +
  								  funcVarCounterLength + 1)*sizeof(char));
  		strcpy(varName, ZZ_FUNCVAR_PREFIX);
 		strcat(varName, funcVarCounterString);
	    string newVarName = zzgetNewVarName(varName);
      	
      	varNames.append(newVarName);
      	
      	for (int i = 1; i < typeIds.size(); i++)
      	  varNames[i] = (*funclo)[i]->getStr();

		// Predicate name is PredicateTemplate::ZZ_RETURN_PREFIX + function name
		char* predName;
		predName = (char *)malloc((strlen(PredicateTemplate::ZZ_RETURN_PREFIX) +
  	    					   strlen(zzfunc->getName()) + 1)*sizeof(char));
		strcpy(predName, PredicateTemplate::ZZ_RETURN_PREFIX);
 		strcat(predName, zzinfixFuncName);
 	
        string unknownIntFuncName =
          	  zzappendWithUnderscore(predName, zzintFuncTypeCounter++);
        zzintFuncList.push_back(ZZUnknownIntFuncInfo(unknownIntFuncName, varNames));
        //funclo->replace(zzinfixFuncName, unknownIntFuncName.c_str());
		free(predName);
		free(varName);
      }
	  free(zzinfixFuncName);
      zzinfixFuncName = NULL;
	}
  	
    zzconsumeToken(zztokenList, ")");
    if (folDbg >= 1) printf(") ");
  }
#line 3456 "fol.tab.c"
    break;

  case 154:
#line 2126 "../src/parser/fol.y"
  {
      // Create a function corresponding to the infix sign
    if (zzfunc != NULL) { zzfuncStack.push(zzfunc); zzfunc = NULL; }
    ++zzfdnumFuncs;
    zzfdfuncName = zzinfixFuncName;
	const FunctionTemplate* t =
      zzgetGenericInternalFunctionTemplate(zzinfixFuncName);
  	zzfunc = new Function(t);
	  // If in a pred. (not LHS of infix pred.), then we know the return type
      // It's the type of the previous variable (getNumTerms() - 1)
	if (zzpred)
      ((FunctionTemplate*)t)->setRetTypeId(
        zzpred->getTermTypeAsInt(zzpred->getNumTerms() - 1), zzdomain);

    ListObj* funclo = new ListObj;
    funclo->append(zzfdfuncName.c_str());
    zzpredFuncListObjs.push(funclo);

      // The first term was added to the previous pred / func
      // So this needs to be switched to the infix function
    moveTermToInfixFunction();
  }
#line 3483 "fol.tab.c"
    break;

  case 155:
#line 2149 "../src/parser/fol.y"
  {
    ListObj* funclo = zzpredFuncListObjs.top();

	  // types are possibly unknown
    bool unknownTypes = false;
	
      // First element is return type
    Array<int> typeIds(zzfunc->getNumTerms() + 1);
    typeIds.append(zzfunc->getRetTypeId());
    if (typeIds[0] <= 0) unknownTypes = true;
		
      // Then term types
	for (int i = 1; i <= zzfunc->getNumTerms(); i++)
	{
      typeIds.append(zzgetTypeId(zzfunc->getTerm(i-1), (*funclo)[i]->getStr()));
      if (typeIds[i] <= 0) unknownTypes = true;
	}

	  // If all types are known
	if (!unknownTypes)
	{
 	  zzsetInternalFuncTypeName(zzinfixFuncName, typeIds);
	}
    else // Not all types are known, delay processing
    {
      Array<string> varNames(typeIds.size());
      	
      char* varName;
      char funcVarCounterString[10];
      int funcVarCounterLength =
      		sprintf(funcVarCounterString, "%d", zzfuncVarCounter);
      varName = (char *)malloc((strlen(ZZ_FUNCVAR_PREFIX) +
  								funcVarCounterLength + 1)*sizeof(char));
  	  strcpy(varName, ZZ_FUNCVAR_PREFIX);
 	  strcat(varName, funcVarCounterString);
	  string newVarName = zzgetNewVarName(varName);
      	
      varNames.append(newVarName);
      	
      for (int i = 1; i < typeIds.size(); i++)
        varNames[i] = (*funclo)[i]->getStr();
		// Predicate name is PredicateTemplate::ZZ_RETURN_PREFIX + function name
      char* predName;
      predName = (char *)malloc((strlen(PredicateTemplate::ZZ_RETURN_PREFIX) +
  	       					     strlen(zzfunc->getName()) + 1)*sizeof(char));
      strcpy(predName, PredicateTemplate::ZZ_RETURN_PREFIX);
      strcat(predName, zzinfixFuncName);
 	
      string unknownIntFuncName =
       	zzappendWithUnderscore(predName, zzintFuncTypeCounter++);
      zzintFuncList.push_back(ZZUnknownIntFuncInfo(unknownIntFuncName, varNames));
        //funclo->replace(zzinfixFuncName, unknownIntFuncName.c_str());
      free(predName);
      free(varName);
    }
    free(zzinfixFuncName);
    zzinfixFuncName = NULL;
  }
#line 3546 "fol.tab.c"
    break;

  case 156:
#line 2211 "../src/parser/fol.y"
  {
    zzconsumeToken(zztokenList, "+");
    if (folDbg >= 1) printf("+ "); 
    zzinfixFuncName = (char *)malloc((strlen(PredicateTemplate::PLUS_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixFuncName, PredicateTemplate::PLUS_NAME);
  }
#line 3558 "fol.tab.c"
    break;

  case 157:
#line 2220 "../src/parser/fol.y"
  {
   	zzconsumeToken(zztokenList, "-");
    if (folDbg >= 1) printf("- "); 
    zzinfixFuncName = (char *)malloc((strlen(PredicateTemplate::MINUS_NAME)
                                      + 1)*sizeof(char));
    strcpy(zzinfixFuncName, PredicateTemplate::MINUS_NAME);
  }
#line 3570 "fol.tab.c"
    break;

  case 158:
#line 2229 "../src/parser/fol.y"
  {
  	zzconsumeToken(zztokenList, "*");
    if (folDbg >= 1) printf("* ");
    zzinfixFuncName = (char *)malloc((strlen(PredicateTemplate::TIMES_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixFuncName, PredicateTemplate::TIMES_NAME);
  }
#line 3582 "fol.tab.c"
    break;

  case 159:
#line 2238 "../src/parser/fol.y"
  {
	zzconsumeToken(zztokenList, "/");
    if (folDbg >= 1) printf("/ ");
    zzinfixFuncName = (char *)malloc((strlen(PredicateTemplate::DIVIDEDBY_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixFuncName, PredicateTemplate::DIVIDEDBY_NAME);
  }
#line 3594 "fol.tab.c"
    break;

  case 160:
#line 2247 "../src/parser/fol.y"
  {
  	zzconsumeToken(zztokenList, "%");
    if (folDbg >= 1) printf("%% ");
    zzinfixFuncName = (char *)malloc((strlen(PredicateTemplate::MOD_NAME)
    								  + 1)*sizeof(char));
  	strcpy(zzinfixFuncName, PredicateTemplate::MOD_NAME);
  }
#line 3606 "fol.tab.c"
    break;


#line 3610 "fol.tab.c"

      default: break;
    }

  return yyok;
# undef yyerrok
# undef YYABORT
# undef YYACCEPT
# undef YYERROR
# undef YYBACKUP
# undef yyclearin
# undef YYRECOVERING
}


static void
yyuserMerge (int yyn, YYSTYPE* yy0, YYSTYPE* yy1)
{
  YYUSE (yy0);
  YYUSE (yy1);

  switch (yyn)
    {

      default: break;
    }
}

                              /* Bison grammar-table manipulation.  */

/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg, int yytype, YYSTYPE *yyvaluep)
{
  YYUSE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yytype, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YYUSE (yytype);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}

/** Number of symbols composing the right hand side of rule #RULE.  */
static inline int
yyrhsLength (yyRuleNum yyrule)
{
  return yyr2[yyrule];
}

static void
yydestroyGLRState (char const *yymsg, yyGLRState *yys)
{
  if (yys->yyresolved)
    yydestruct (yymsg, yystos[yys->yylrState],
                &yys->yysemantics.yysval);
  else
    {
#if YYDEBUG
      if (yydebug)
        {
          if (yys->yysemantics.yyfirstVal)
            YY_FPRINTF ((stderr, "%s unresolved", yymsg));
          else
            YY_FPRINTF ((stderr, "%s incomplete", yymsg));
          YY_SYMBOL_PRINT ("", yystos[yys->yylrState], YY_NULLPTR, &yys->yyloc);
        }
#endif

      if (yys->yysemantics.yyfirstVal)
        {
          yySemanticOption *yyoption = yys->yysemantics.yyfirstVal;
          yyGLRState *yyrh;
          int yyn;
          for (yyrh = yyoption->yystate, yyn = yyrhsLength (yyoption->yyrule);
               yyn > 0;
               yyrh = yyrh->yypred, yyn -= 1)
            yydestroyGLRState (yymsg, yyrh);
        }
    }
}

/** Left-hand-side symbol for rule #YYRULE.  */
static inline yySymbol
yylhsNonterm (yyRuleNum yyrule)
{
  return yyr1[yyrule];
}

#define yypact_value_is_default(Yyn) \
  ((Yyn) == YYPACT_NINF)

/** True iff LR state YYSTATE has only a default reduction (regardless
 *  of token).  */
static inline yybool
yyisDefaultedState (yyStateNum yystate)
{
  return yypact_value_is_default (yypact[yystate]);
}

/** The default reduction for YYSTATE, assuming it has one.  */
static inline yyRuleNum
yydefaultAction (yyStateNum yystate)
{
  return yydefact[yystate];
}

#define yytable_value_is_error(Yyn) \
  0

/** The action to take in YYSTATE on seeing YYTOKEN.
 *  Result R means
 *    R < 0:  Reduce on rule -R.
 *    R = 0:  Error.
 *    R > 0:  Shift to state R.
 *  Set *YYCONFLICTS to a pointer into yyconfl to a 0-terminated list
 *  of conflicting reductions.
 */
static inline int
yygetLRActions (yyStateNum yystate, yySymbol yytoken, const short** yyconflicts)
{
  int yyindex = yypact[yystate] + yytoken;
  if (yyisDefaultedState (yystate)
      || yyindex < 0 || YYLAST < yyindex || yycheck[yyindex] != yytoken)
    {
      *yyconflicts = yyconfl;
      return -yydefact[yystate];
    }
  else if (! yytable_value_is_error (yytable[yyindex]))
    {
      *yyconflicts = yyconfl + yyconflp[yyindex];
      return yytable[yyindex];
    }
  else
    {
      *yyconflicts = yyconfl + yyconflp[yyindex];
      return 0;
    }
}

/** Compute post-reduction state.
 * \param yystate   the current state
 * \param yysym     the nonterminal to push on the stack
 */
static inline yyStateNum
yyLRgotoState (yyStateNum yystate, yySymbol yysym)
{
  int yyr = yypgoto[yysym - YYNTOKENS] + yystate;
  if (0 <= yyr && yyr <= YYLAST && yycheck[yyr] == yystate)
    return yytable[yyr];
  else
    return yydefgoto[yysym - YYNTOKENS];
}

static inline yybool
yyisShiftAction (int yyaction)
{
  return 0 < yyaction;
}

static inline yybool
yyisErrorAction (int yyaction)
{
  return yyaction == 0;
}

                                /* GLRStates */

/** Return a fresh GLRStackItem in YYSTACKP.  The item is an LR state
 *  if YYISSTATE, and otherwise a semantic option.  Callers should call
 *  YY_RESERVE_GLRSTACK afterwards to make sure there is sufficient
 *  headroom.  */

static inline yyGLRStackItem*
yynewGLRStackItem (yyGLRStack* yystackp, yybool yyisState)
{
  yyGLRStackItem* yynewItem = yystackp->yynextFree;
  yystackp->yyspaceLeft -= 1;
  yystackp->yynextFree += 1;
  yynewItem->yystate.yyisState = yyisState;
  return yynewItem;
}

/** Add a new semantic action that will execute the action for rule
 *  YYRULE on the semantic values in YYRHS to the list of
 *  alternative actions for YYSTATE.  Assumes that YYRHS comes from
 *  stack #YYK of *YYSTACKP. */
static void
yyaddDeferredAction (yyGLRStack* yystackp, ptrdiff_t yyk, yyGLRState* yystate,
                     yyGLRState* yyrhs, yyRuleNum yyrule)
{
  yySemanticOption* yynewOption =
    &yynewGLRStackItem (yystackp, yyfalse)->yyoption;
  YY_ASSERT (!yynewOption->yyisState);
  yynewOption->yystate = yyrhs;
  yynewOption->yyrule = yyrule;
  if (yystackp->yytops.yylookaheadNeeds[yyk])
    {
      yynewOption->yyrawchar = yychar;
      yynewOption->yyval = yylval;
    }
  else
    yynewOption->yyrawchar = YYEMPTY;
  yynewOption->yynext = yystate->yysemantics.yyfirstVal;
  yystate->yysemantics.yyfirstVal = yynewOption;

  YY_RESERVE_GLRSTACK (yystackp);
}

                                /* GLRStacks */

/** Initialize YYSET to a singleton set containing an empty stack.  */
static yybool
yyinitStateSet (yyGLRStateSet* yyset)
{
  yyset->yysize = 1;
  yyset->yycapacity = 16;
  yyset->yystates
    = YY_CAST (yyGLRState**,
               YYMALLOC (YY_CAST (size_t, yyset->yycapacity)
                         * sizeof yyset->yystates[0]));
  if (! yyset->yystates)
    return yyfalse;
  yyset->yystates[0] = YY_NULLPTR;
  yyset->yylookaheadNeeds
    = YY_CAST (yybool*,
               YYMALLOC (YY_CAST (size_t, yyset->yycapacity)
                         * sizeof yyset->yylookaheadNeeds[0]));
  if (! yyset->yylookaheadNeeds)
    {
      YYFREE (yyset->yystates);
      return yyfalse;
    }
  memset (yyset->yylookaheadNeeds,
          0,
          YY_CAST (size_t, yyset->yycapacity) * sizeof yyset->yylookaheadNeeds[0]);
  return yytrue;
}

static void yyfreeStateSet (yyGLRStateSet* yyset)
{
  YYFREE (yyset->yystates);
  YYFREE (yyset->yylookaheadNeeds);
}

/** Initialize *YYSTACKP to a single empty stack, with total maximum
 *  capacity for all stacks of YYSIZE.  */
static yybool
yyinitGLRStack (yyGLRStack* yystackp, ptrdiff_t yysize)
{
  yystackp->yyerrState = 0;
  yynerrs = 0;
  yystackp->yyspaceLeft = yysize;
  yystackp->yyitems
    = YY_CAST (yyGLRStackItem*,
               YYMALLOC (YY_CAST (size_t, yysize)
                         * sizeof yystackp->yynextFree[0]));
  if (!yystackp->yyitems)
    return yyfalse;
  yystackp->yynextFree = yystackp->yyitems;
  yystackp->yysplitPoint = YY_NULLPTR;
  yystackp->yylastDeleted = YY_NULLPTR;
  return yyinitStateSet (&yystackp->yytops);
}


#if YYSTACKEXPANDABLE
# define YYRELOC(YYFROMITEMS, YYTOITEMS, YYX, YYTYPE)                   \
  &((YYTOITEMS)                                                         \
    - ((YYFROMITEMS) - YY_REINTERPRET_CAST (yyGLRStackItem*, (YYX))))->YYTYPE

/** If *YYSTACKP is expandable, extend it.  WARNING: Pointers into the
    stack from outside should be considered invalid after this call.
    We always expand when there are 1 or fewer items left AFTER an
    allocation, so that we can avoid having external pointers exist
    across an allocation.  */
static void
yyexpandGLRStack (yyGLRStack* yystackp)
{
  yyGLRStackItem* yynewItems;
  yyGLRStackItem* yyp0, *yyp1;
  ptrdiff_t yynewSize;
  ptrdiff_t yyn;
  ptrdiff_t yysize = yystackp->yynextFree - yystackp->yyitems;
  if (YYMAXDEPTH - YYHEADROOM < yysize)
    yyMemoryExhausted (yystackp);
  yynewSize = 2*yysize;
  if (YYMAXDEPTH < yynewSize)
    yynewSize = YYMAXDEPTH;
  yynewItems
    = YY_CAST (yyGLRStackItem*,
               YYMALLOC (YY_CAST (size_t, yynewSize)
                         * sizeof yynewItems[0]));
  if (! yynewItems)
    yyMemoryExhausted (yystackp);
  for (yyp0 = yystackp->yyitems, yyp1 = yynewItems, yyn = yysize;
       0 < yyn;
       yyn -= 1, yyp0 += 1, yyp1 += 1)
    {
      *yyp1 = *yyp0;
      if (*YY_REINTERPRET_CAST (yybool *, yyp0))
        {
          yyGLRState* yys0 = &yyp0->yystate;
          yyGLRState* yys1 = &yyp1->yystate;
          if (yys0->yypred != YY_NULLPTR)
            yys1->yypred =
              YYRELOC (yyp0, yyp1, yys0->yypred, yystate);
          if (! yys0->yyresolved && yys0->yysemantics.yyfirstVal != YY_NULLPTR)
            yys1->yysemantics.yyfirstVal =
              YYRELOC (yyp0, yyp1, yys0->yysemantics.yyfirstVal, yyoption);
        }
      else
        {
          yySemanticOption* yyv0 = &yyp0->yyoption;
          yySemanticOption* yyv1 = &yyp1->yyoption;
          if (yyv0->yystate != YY_NULLPTR)
            yyv1->yystate = YYRELOC (yyp0, yyp1, yyv0->yystate, yystate);
          if (yyv0->yynext != YY_NULLPTR)
            yyv1->yynext = YYRELOC (yyp0, yyp1, yyv0->yynext, yyoption);
        }
    }
  if (yystackp->yysplitPoint != YY_NULLPTR)
    yystackp->yysplitPoint = YYRELOC (yystackp->yyitems, yynewItems,
                                      yystackp->yysplitPoint, yystate);

  for (yyn = 0; yyn < yystackp->yytops.yysize; yyn += 1)
    if (yystackp->yytops.yystates[yyn] != YY_NULLPTR)
      yystackp->yytops.yystates[yyn] =
        YYRELOC (yystackp->yyitems, yynewItems,
                 yystackp->yytops.yystates[yyn], yystate);
  YYFREE (yystackp->yyitems);
  yystackp->yyitems = yynewItems;
  yystackp->yynextFree = yynewItems + yysize;
  yystackp->yyspaceLeft = yynewSize - yysize;
}
#endif

static void
yyfreeGLRStack (yyGLRStack* yystackp)
{
  YYFREE (yystackp->yyitems);
  yyfreeStateSet (&yystackp->yytops);
}

/** Assuming that YYS is a GLRState somewhere on *YYSTACKP, update the
 *  splitpoint of *YYSTACKP, if needed, so that it is at least as deep as
 *  YYS.  */
static inline void
yyupdateSplit (yyGLRStack* yystackp, yyGLRState* yys)
{
  if (yystackp->yysplitPoint != YY_NULLPTR && yystackp->yysplitPoint > yys)
    yystackp->yysplitPoint = yys;
}

/** Invalidate stack #YYK in *YYSTACKP.  */
static inline void
yymarkStackDeleted (yyGLRStack* yystackp, ptrdiff_t yyk)
{
  if (yystackp->yytops.yystates[yyk] != YY_NULLPTR)
    yystackp->yylastDeleted = yystackp->yytops.yystates[yyk];
  yystackp->yytops.yystates[yyk] = YY_NULLPTR;
}

/** Undelete the last stack in *YYSTACKP that was marked as deleted.  Can
    only be done once after a deletion, and only when all other stacks have
    been deleted.  */
static void
yyundeleteLastStack (yyGLRStack* yystackp)
{
  if (yystackp->yylastDeleted == YY_NULLPTR || yystackp->yytops.yysize != 0)
    return;
  yystackp->yytops.yystates[0] = yystackp->yylastDeleted;
  yystackp->yytops.yysize = 1;
  YY_DPRINTF ((stderr, "Restoring last deleted stack as stack #0.\n"));
  yystackp->yylastDeleted = YY_NULLPTR;
}

static inline void
yyremoveDeletes (yyGLRStack* yystackp)
{
  ptrdiff_t yyi, yyj;
  yyi = yyj = 0;
  while (yyj < yystackp->yytops.yysize)
    {
      if (yystackp->yytops.yystates[yyi] == YY_NULLPTR)
        {
          if (yyi == yyj)
            YY_DPRINTF ((stderr, "Removing dead stacks.\n"));
          yystackp->yytops.yysize -= 1;
        }
      else
        {
          yystackp->yytops.yystates[yyj] = yystackp->yytops.yystates[yyi];
          /* In the current implementation, it's unnecessary to copy
             yystackp->yytops.yylookaheadNeeds[yyi] since, after
             yyremoveDeletes returns, the parser immediately either enters
             deterministic operation or shifts a token.  However, it doesn't
             hurt, and the code might evolve to need it.  */
          yystackp->yytops.yylookaheadNeeds[yyj] =
            yystackp->yytops.yylookaheadNeeds[yyi];
          if (yyj != yyi)
            YY_DPRINTF ((stderr, "Rename stack %ld -> %ld.\n",
                        YY_CAST (long, yyi), YY_CAST (long, yyj)));
          yyj += 1;
        }
      yyi += 1;
    }
}

/** Shift to a new state on stack #YYK of *YYSTACKP, corresponding to LR
 * state YYLRSTATE, at input position YYPOSN, with (resolved) semantic
 * value *YYVALP and source location *YYLOCP.  */
static inline void
yyglrShift (yyGLRStack* yystackp, ptrdiff_t yyk, yyStateNum yylrState,
            ptrdiff_t yyposn,
            YYSTYPE* yyvalp)
{
  yyGLRState* yynewState = &yynewGLRStackItem (yystackp, yytrue)->yystate;

  yynewState->yylrState = yylrState;
  yynewState->yyposn = yyposn;
  yynewState->yyresolved = yytrue;
  yynewState->yypred = yystackp->yytops.yystates[yyk];
  yynewState->yysemantics.yysval = *yyvalp;
  yystackp->yytops.yystates[yyk] = yynewState;

  YY_RESERVE_GLRSTACK (yystackp);
}

/** Shift stack #YYK of *YYSTACKP, to a new state corresponding to LR
 *  state YYLRSTATE, at input position YYPOSN, with the (unresolved)
 *  semantic value of YYRHS under the action for YYRULE.  */
static inline void
yyglrShiftDefer (yyGLRStack* yystackp, ptrdiff_t yyk, yyStateNum yylrState,
                 ptrdiff_t yyposn, yyGLRState* yyrhs, yyRuleNum yyrule)
{
  yyGLRState* yynewState = &yynewGLRStackItem (yystackp, yytrue)->yystate;
  YY_ASSERT (yynewState->yyisState);

  yynewState->yylrState = yylrState;
  yynewState->yyposn = yyposn;
  yynewState->yyresolved = yyfalse;
  yynewState->yypred = yystackp->yytops.yystates[yyk];
  yynewState->yysemantics.yyfirstVal = YY_NULLPTR;
  yystackp->yytops.yystates[yyk] = yynewState;

  /* Invokes YY_RESERVE_GLRSTACK.  */
  yyaddDeferredAction (yystackp, yyk, yynewState, yyrhs, yyrule);
}

#if !YYDEBUG
# define YY_REDUCE_PRINT(Args)
#else
# define YY_REDUCE_PRINT(Args)          \
  do {                                  \
    if (yydebug)                        \
      yy_reduce_print Args;             \
  } while (0)

/*----------------------------------------------------------------------.
| Report that stack #YYK of *YYSTACKP is going to be reduced by YYRULE. |
`----------------------------------------------------------------------*/

static inline void
yy_reduce_print (yybool yynormal, yyGLRStackItem* yyvsp, ptrdiff_t yyk,
                 yyRuleNum yyrule)
{
  int yynrhs = yyrhsLength (yyrule);
  int yyi;
  YY_FPRINTF ((stderr, "Reducing stack %ld by rule %d (line %d):\n",
               YY_CAST (long, yyk), yyrule - 1, yyrline[yyrule]));
  if (! yynormal)
    yyfillin (yyvsp, 1, -yynrhs);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YY_FPRINTF ((stderr, "   $%d = ", yyi + 1));
      yy_symbol_print (stderr,
                       yystos[yyvsp[yyi - yynrhs + 1].yystate.yylrState],
                       &yyvsp[yyi - yynrhs + 1].yystate.yysemantics.yysval                       );
      if (!yyvsp[yyi - yynrhs + 1].yystate.yyresolved)
        YY_FPRINTF ((stderr, " (unresolved)"));
      YY_FPRINTF ((stderr, "\n"));
    }
}
#endif

/** Pop the symbols consumed by reduction #YYRULE from the top of stack
 *  #YYK of *YYSTACKP, and perform the appropriate semantic action on their
 *  semantic values.  Assumes that all ambiguities in semantic values
 *  have been previously resolved.  Set *YYVALP to the resulting value,
 *  and *YYLOCP to the computed location (if any).  Return value is as
 *  for userAction.  */
static inline YYRESULTTAG
yydoAction (yyGLRStack* yystackp, ptrdiff_t yyk, yyRuleNum yyrule,
            YYSTYPE* yyvalp)
{
  int yynrhs = yyrhsLength (yyrule);

  if (yystackp->yysplitPoint == YY_NULLPTR)
    {
      /* Standard special case: single stack.  */
      yyGLRStackItem* yyrhs
        = YY_REINTERPRET_CAST (yyGLRStackItem*, yystackp->yytops.yystates[yyk]);
      YY_ASSERT (yyk == 0);
      yystackp->yynextFree -= yynrhs;
      yystackp->yyspaceLeft += yynrhs;
      yystackp->yytops.yystates[0] = & yystackp->yynextFree[-1].yystate;
      YY_REDUCE_PRINT ((yytrue, yyrhs, yyk, yyrule));
      return yyuserAction (yyrule, yynrhs, yyrhs, yystackp,
                           yyvalp);
    }
  else
    {
      yyGLRStackItem yyrhsVals[YYMAXRHS + YYMAXLEFT + 1];
      yyGLRState* yys = yyrhsVals[YYMAXRHS + YYMAXLEFT].yystate.yypred
        = yystackp->yytops.yystates[yyk];
      int yyi;
      for (yyi = 0; yyi < yynrhs; yyi += 1)
        {
          yys = yys->yypred;
          YY_ASSERT (yys);
        }
      yyupdateSplit (yystackp, yys);
      yystackp->yytops.yystates[yyk] = yys;
      YY_REDUCE_PRINT ((yyfalse, yyrhsVals + YYMAXRHS + YYMAXLEFT - 1, yyk, yyrule));
      return yyuserAction (yyrule, yynrhs, yyrhsVals + YYMAXRHS + YYMAXLEFT - 1,
                           yystackp, yyvalp);
    }
}

/** Pop items off stack #YYK of *YYSTACKP according to grammar rule YYRULE,
 *  and push back on the resulting nonterminal symbol.  Perform the
 *  semantic action associated with YYRULE and store its value with the
 *  newly pushed state, if YYFORCEEVAL or if *YYSTACKP is currently
 *  unambiguous.  Otherwise, store the deferred semantic action with
 *  the new state.  If the new state would have an identical input
 *  position, LR state, and predecessor to an existing state on the stack,
 *  it is identified with that existing state, eliminating stack #YYK from
 *  *YYSTACKP.  In this case, the semantic value is
 *  added to the options for the existing state's semantic value.
 */
static inline YYRESULTTAG
yyglrReduce (yyGLRStack* yystackp, ptrdiff_t yyk, yyRuleNum yyrule,
             yybool yyforceEval)
{
  ptrdiff_t yyposn = yystackp->yytops.yystates[yyk]->yyposn;

  if (yyforceEval || yystackp->yysplitPoint == YY_NULLPTR)
    {
      YYSTYPE yysval;

      YYRESULTTAG yyflag = yydoAction (yystackp, yyk, yyrule, &yysval);
      if (yyflag == yyerr && yystackp->yysplitPoint != YY_NULLPTR)
        YY_DPRINTF ((stderr,
                     "Parse on stack %ld rejected by rule %d (line %d).\n",
                     YY_CAST (long, yyk), yyrule - 1, yyrline[yyrule - 1]));
      if (yyflag != yyok)
        return yyflag;
      YY_SYMBOL_PRINT ("-> $$ =", yyr1[yyrule], &yysval, &yyloc);
      yyglrShift (yystackp, yyk,
                  yyLRgotoState (yystackp->yytops.yystates[yyk]->yylrState,
                                 yylhsNonterm (yyrule)),
                  yyposn, &yysval);
    }
  else
    {
      ptrdiff_t yyi;
      int yyn;
      yyGLRState* yys, *yys0 = yystackp->yytops.yystates[yyk];
      yyStateNum yynewLRState;

      for (yys = yystackp->yytops.yystates[yyk], yyn = yyrhsLength (yyrule);
           0 < yyn; yyn -= 1)
        {
          yys = yys->yypred;
          YY_ASSERT (yys);
        }
      yyupdateSplit (yystackp, yys);
      yynewLRState = yyLRgotoState (yys->yylrState, yylhsNonterm (yyrule));
      YY_DPRINTF ((stderr,
                   "Reduced stack %ld by rule %d (line %d); action deferred.  "
                   "Now in state %d.\n",
                   YY_CAST (long, yyk), yyrule - 1, yyrline[yyrule - 1],
                   yynewLRState));
      for (yyi = 0; yyi < yystackp->yytops.yysize; yyi += 1)
        if (yyi != yyk && yystackp->yytops.yystates[yyi] != YY_NULLPTR)
          {
            yyGLRState *yysplit = yystackp->yysplitPoint;
            yyGLRState *yyp = yystackp->yytops.yystates[yyi];
            while (yyp != yys && yyp != yysplit && yyp->yyposn >= yyposn)
              {
                if (yyp->yylrState == yynewLRState && yyp->yypred == yys)
                  {
                    yyaddDeferredAction (yystackp, yyk, yyp, yys0, yyrule);
                    yymarkStackDeleted (yystackp, yyk);
                    YY_DPRINTF ((stderr, "Merging stack %ld into stack %ld.\n",
                                 YY_CAST (long, yyk), YY_CAST (long, yyi)));
                    return yyok;
                  }
                yyp = yyp->yypred;
              }
          }
      yystackp->yytops.yystates[yyk] = yys;
      yyglrShiftDefer (yystackp, yyk, yynewLRState, yyposn, yys0, yyrule);
    }
  return yyok;
}

static ptrdiff_t
yysplitStack (yyGLRStack* yystackp, ptrdiff_t yyk)
{
  if (yystackp->yysplitPoint == YY_NULLPTR)
    {
      YY_ASSERT (yyk == 0);
      yystackp->yysplitPoint = yystackp->yytops.yystates[yyk];
    }
  if (yystackp->yytops.yycapacity <= yystackp->yytops.yysize)
    {
      ptrdiff_t state_size = sizeof yystackp->yytops.yystates[0];
      ptrdiff_t half_max_capacity = YYSIZEMAX / 2 / state_size;
      if (half_max_capacity < yystackp->yytops.yycapacity)
        yyMemoryExhausted (yystackp);
      yystackp->yytops.yycapacity *= 2;

      {
        yyGLRState** yynewStates
          = YY_CAST (yyGLRState**,
                     YYREALLOC (yystackp->yytops.yystates,
                                (YY_CAST (size_t, yystackp->yytops.yycapacity)
                                 * sizeof yynewStates[0])));
        if (yynewStates == YY_NULLPTR)
          yyMemoryExhausted (yystackp);
        yystackp->yytops.yystates = yynewStates;
      }

      {
        yybool* yynewLookaheadNeeds
          = YY_CAST (yybool*,
                     YYREALLOC (yystackp->yytops.yylookaheadNeeds,
                                (YY_CAST (size_t, yystackp->yytops.yycapacity)
                                 * sizeof yynewLookaheadNeeds[0])));
        if (yynewLookaheadNeeds == YY_NULLPTR)
          yyMemoryExhausted (yystackp);
        yystackp->yytops.yylookaheadNeeds = yynewLookaheadNeeds;
      }
    }
  yystackp->yytops.yystates[yystackp->yytops.yysize]
    = yystackp->yytops.yystates[yyk];
  yystackp->yytops.yylookaheadNeeds[yystackp->yytops.yysize]
    = yystackp->yytops.yylookaheadNeeds[yyk];
  yystackp->yytops.yysize += 1;
  return yystackp->yytops.yysize - 1;
}

/** True iff YYY0 and YYY1 represent identical options at the top level.
 *  That is, they represent the same rule applied to RHS symbols
 *  that produce the same terminal symbols.  */
static yybool
yyidenticalOptions (yySemanticOption* yyy0, yySemanticOption* yyy1)
{
  if (yyy0->yyrule == yyy1->yyrule)
    {
      yyGLRState *yys0, *yys1;
      int yyn;
      for (yys0 = yyy0->yystate, yys1 = yyy1->yystate,
           yyn = yyrhsLength (yyy0->yyrule);
           yyn > 0;
           yys0 = yys0->yypred, yys1 = yys1->yypred, yyn -= 1)
        if (yys0->yyposn != yys1->yyposn)
          return yyfalse;
      return yytrue;
    }
  else
    return yyfalse;
}

/** Assuming identicalOptions (YYY0,YYY1), destructively merge the
 *  alternative semantic values for the RHS-symbols of YYY1 and YYY0.  */
static void
yymergeOptionSets (yySemanticOption* yyy0, yySemanticOption* yyy1)
{
  yyGLRState *yys0, *yys1;
  int yyn;
  for (yys0 = yyy0->yystate, yys1 = yyy1->yystate,
       yyn = yyrhsLength (yyy0->yyrule);
       0 < yyn;
       yys0 = yys0->yypred, yys1 = yys1->yypred, yyn -= 1)
    {
      if (yys0 == yys1)
        break;
      else if (yys0->yyresolved)
        {
          yys1->yyresolved = yytrue;
          yys1->yysemantics.yysval = yys0->yysemantics.yysval;
        }
      else if (yys1->yyresolved)
        {
          yys0->yyresolved = yytrue;
          yys0->yysemantics.yysval = yys1->yysemantics.yysval;
        }
      else
        {
          yySemanticOption** yyz0p = &yys0->yysemantics.yyfirstVal;
          yySemanticOption* yyz1 = yys1->yysemantics.yyfirstVal;
          while (yytrue)
            {
              if (yyz1 == *yyz0p || yyz1 == YY_NULLPTR)
                break;
              else if (*yyz0p == YY_NULLPTR)
                {
                  *yyz0p = yyz1;
                  break;
                }
              else if (*yyz0p < yyz1)
                {
                  yySemanticOption* yyz = *yyz0p;
                  *yyz0p = yyz1;
                  yyz1 = yyz1->yynext;
                  (*yyz0p)->yynext = yyz;
                }
              yyz0p = &(*yyz0p)->yynext;
            }
          yys1->yysemantics.yyfirstVal = yys0->yysemantics.yyfirstVal;
        }
    }
}

/** Y0 and Y1 represent two possible actions to take in a given
 *  parsing state; return 0 if no combination is possible,
 *  1 if user-mergeable, 2 if Y0 is preferred, 3 if Y1 is preferred.  */
static int
yypreference (yySemanticOption* y0, yySemanticOption* y1)
{
  yyRuleNum r0 = y0->yyrule, r1 = y1->yyrule;
  int p0 = yydprec[r0], p1 = yydprec[r1];

  if (p0 == p1)
    {
      if (yymerger[r0] == 0 || yymerger[r0] != yymerger[r1])
        return 0;
      else
        return 1;
    }
  if (p0 == 0 || p1 == 0)
    return 0;
  if (p0 < p1)
    return 3;
  if (p1 < p0)
    return 2;
  return 0;
}

static YYRESULTTAG yyresolveValue (yyGLRState* yys,
                                   yyGLRStack* yystackp);


/** Resolve the previous YYN states starting at and including state YYS
 *  on *YYSTACKP. If result != yyok, some states may have been left
 *  unresolved possibly with empty semantic option chains.  Regardless
 *  of whether result = yyok, each state has been left with consistent
 *  data so that yydestroyGLRState can be invoked if necessary.  */
static YYRESULTTAG
yyresolveStates (yyGLRState* yys, int yyn,
                 yyGLRStack* yystackp)
{
  if (0 < yyn)
    {
      YY_ASSERT (yys->yypred);
      YYCHK (yyresolveStates (yys->yypred, yyn-1, yystackp));
      if (! yys->yyresolved)
        YYCHK (yyresolveValue (yys, yystackp));
    }
  return yyok;
}

/** Resolve the states for the RHS of YYOPT on *YYSTACKP, perform its
 *  user action, and return the semantic value and location in *YYVALP
 *  and *YYLOCP.  Regardless of whether result = yyok, all RHS states
 *  have been destroyed (assuming the user action destroys all RHS
 *  semantic values if invoked).  */
static YYRESULTTAG
yyresolveAction (yySemanticOption* yyopt, yyGLRStack* yystackp,
                 YYSTYPE* yyvalp)
{
  yyGLRStackItem yyrhsVals[YYMAXRHS + YYMAXLEFT + 1];
  int yynrhs = yyrhsLength (yyopt->yyrule);
  YYRESULTTAG yyflag =
    yyresolveStates (yyopt->yystate, yynrhs, yystackp);
  if (yyflag != yyok)
    {
      yyGLRState *yys;
      for (yys = yyopt->yystate; yynrhs > 0; yys = yys->yypred, yynrhs -= 1)
        yydestroyGLRState ("Cleanup: popping", yys);
      return yyflag;
    }

  yyrhsVals[YYMAXRHS + YYMAXLEFT].yystate.yypred = yyopt->yystate;
  {
    int yychar_current = yychar;
    YYSTYPE yylval_current = yylval;
    yychar = yyopt->yyrawchar;
    yylval = yyopt->yyval;
    yyflag = yyuserAction (yyopt->yyrule, yynrhs,
                           yyrhsVals + YYMAXRHS + YYMAXLEFT - 1,
                           yystackp, yyvalp);
    yychar = yychar_current;
    yylval = yylval_current;
  }
  return yyflag;
}

#if YYDEBUG
static void
yyreportTree (yySemanticOption* yyx, int yyindent)
{
  int yynrhs = yyrhsLength (yyx->yyrule);
  int yyi;
  yyGLRState* yys;
  yyGLRState* yystates[1 + YYMAXRHS];
  yyGLRState yyleftmost_state;

  for (yyi = yynrhs, yys = yyx->yystate; 0 < yyi; yyi -= 1, yys = yys->yypred)
    yystates[yyi] = yys;
  if (yys == YY_NULLPTR)
    {
      yyleftmost_state.yyposn = 0;
      yystates[0] = &yyleftmost_state;
    }
  else
    yystates[0] = yys;

  if (yyx->yystate->yyposn < yys->yyposn + 1)
    YY_FPRINTF ((stderr, "%*s%s -> <Rule %d, empty>\n",
                 yyindent, "", yytokenName (yylhsNonterm (yyx->yyrule)),
                 yyx->yyrule - 1));
  else
    YY_FPRINTF ((stderr, "%*s%s -> <Rule %d, tokens %ld .. %ld>\n",
                 yyindent, "", yytokenName (yylhsNonterm (yyx->yyrule)),
                 yyx->yyrule - 1, YY_CAST (long, yys->yyposn + 1),
                 YY_CAST (long, yyx->yystate->yyposn)));
  for (yyi = 1; yyi <= yynrhs; yyi += 1)
    {
      if (yystates[yyi]->yyresolved)
        {
          if (yystates[yyi-1]->yyposn+1 > yystates[yyi]->yyposn)
            YY_FPRINTF ((stderr, "%*s%s <empty>\n", yyindent+2, "",
                         yytokenName (yystos[yystates[yyi]->yylrState])));
          else
            YY_FPRINTF ((stderr, "%*s%s <tokens %ld .. %ld>\n", yyindent+2, "",
                         yytokenName (yystos[yystates[yyi]->yylrState]),
                         YY_CAST (long, yystates[yyi-1]->yyposn + 1),
                         YY_CAST (long, yystates[yyi]->yyposn)));
        }
      else
        yyreportTree (yystates[yyi]->yysemantics.yyfirstVal, yyindent+2);
    }
}
#endif

static YYRESULTTAG
yyreportAmbiguity (yySemanticOption* yyx0,
                   yySemanticOption* yyx1)
{
  YYUSE (yyx0);
  YYUSE (yyx1);

#if YYDEBUG
  YY_FPRINTF ((stderr, "Ambiguity detected.\n"));
  YY_FPRINTF ((stderr, "Option 1,\n"));
  yyreportTree (yyx0, 2);
  YY_FPRINTF ((stderr, "\nOption 2,\n"));
  yyreportTree (yyx1, 2);
  YY_FPRINTF ((stderr, "\n"));
#endif

  yyerror (YY_("syntax is ambiguous"));
  return yyabort;
}

/** Resolve the ambiguity represented in state YYS in *YYSTACKP,
 *  perform the indicated actions, and set the semantic value of YYS.
 *  If result != yyok, the chain of semantic options in YYS has been
 *  cleared instead or it has been left unmodified except that
 *  redundant options may have been removed.  Regardless of whether
 *  result = yyok, YYS has been left with consistent data so that
 *  yydestroyGLRState can be invoked if necessary.  */
static YYRESULTTAG
yyresolveValue (yyGLRState* yys, yyGLRStack* yystackp)
{
  yySemanticOption* yyoptionList = yys->yysemantics.yyfirstVal;
  yySemanticOption* yybest = yyoptionList;
  yySemanticOption** yypp;
  yybool yymerge = yyfalse;
  YYSTYPE yysval;
  YYRESULTTAG yyflag;

  for (yypp = &yyoptionList->yynext; *yypp != YY_NULLPTR; )
    {
      yySemanticOption* yyp = *yypp;

      if (yyidenticalOptions (yybest, yyp))
        {
          yymergeOptionSets (yybest, yyp);
          *yypp = yyp->yynext;
        }
      else
        {
          switch (yypreference (yybest, yyp))
            {
            case 0:
              return yyreportAmbiguity (yybest, yyp);
              break;
            case 1:
              yymerge = yytrue;
              break;
            case 2:
              break;
            case 3:
              yybest = yyp;
              yymerge = yyfalse;
              break;
            default:
              /* This cannot happen so it is not worth a YY_ASSERT (yyfalse),
                 but some compilers complain if the default case is
                 omitted.  */
              break;
            }
          yypp = &yyp->yynext;
        }
    }

  if (yymerge)
    {
      yySemanticOption* yyp;
      int yyprec = yydprec[yybest->yyrule];
      yyflag = yyresolveAction (yybest, yystackp, &yysval);
      if (yyflag == yyok)
        for (yyp = yybest->yynext; yyp != YY_NULLPTR; yyp = yyp->yynext)
          {
            if (yyprec == yydprec[yyp->yyrule])
              {
                YYSTYPE yysval_other;
                yyflag = yyresolveAction (yyp, yystackp, &yysval_other);
                if (yyflag != yyok)
                  {
                    yydestruct ("Cleanup: discarding incompletely merged value for",
                                yystos[yys->yylrState],
                                &yysval);
                    break;
                  }
                yyuserMerge (yymerger[yyp->yyrule], &yysval, &yysval_other);
              }
          }
    }
  else
    yyflag = yyresolveAction (yybest, yystackp, &yysval);

  if (yyflag == yyok)
    {
      yys->yyresolved = yytrue;
      yys->yysemantics.yysval = yysval;
    }
  else
    yys->yysemantics.yyfirstVal = YY_NULLPTR;
  return yyflag;
}

static YYRESULTTAG
yyresolveStack (yyGLRStack* yystackp)
{
  if (yystackp->yysplitPoint != YY_NULLPTR)
    {
      yyGLRState* yys;
      int yyn;

      for (yyn = 0, yys = yystackp->yytops.yystates[0];
           yys != yystackp->yysplitPoint;
           yys = yys->yypred, yyn += 1)
        continue;
      YYCHK (yyresolveStates (yystackp->yytops.yystates[0], yyn, yystackp
                             ));
    }
  return yyok;
}

static void
yycompressStack (yyGLRStack* yystackp)
{
  yyGLRState* yyp, *yyq, *yyr;

  if (yystackp->yytops.yysize != 1 || yystackp->yysplitPoint == YY_NULLPTR)
    return;

  for (yyp = yystackp->yytops.yystates[0], yyq = yyp->yypred, yyr = YY_NULLPTR;
       yyp != yystackp->yysplitPoint;
       yyr = yyp, yyp = yyq, yyq = yyp->yypred)
    yyp->yypred = yyr;

  yystackp->yyspaceLeft += yystackp->yynextFree - yystackp->yyitems;
  yystackp->yynextFree = YY_REINTERPRET_CAST (yyGLRStackItem*, yystackp->yysplitPoint) + 1;
  yystackp->yyspaceLeft -= yystackp->yynextFree - yystackp->yyitems;
  yystackp->yysplitPoint = YY_NULLPTR;
  yystackp->yylastDeleted = YY_NULLPTR;

  while (yyr != YY_NULLPTR)
    {
      yystackp->yynextFree->yystate = *yyr;
      yyr = yyr->yypred;
      yystackp->yynextFree->yystate.yypred = &yystackp->yynextFree[-1].yystate;
      yystackp->yytops.yystates[0] = &yystackp->yynextFree->yystate;
      yystackp->yynextFree += 1;
      yystackp->yyspaceLeft -= 1;
    }
}

static YYRESULTTAG
yyprocessOneStack (yyGLRStack* yystackp, ptrdiff_t yyk,
                   ptrdiff_t yyposn)
{
  while (yystackp->yytops.yystates[yyk] != YY_NULLPTR)
    {
      yyStateNum yystate = yystackp->yytops.yystates[yyk]->yylrState;
      YY_DPRINTF ((stderr, "Stack %ld Entering state %d\n",
                   YY_CAST (long, yyk), yystate));

      YY_ASSERT (yystate != YYFINAL);

      if (yyisDefaultedState (yystate))
        {
          YYRESULTTAG yyflag;
          yyRuleNum yyrule = yydefaultAction (yystate);
          if (yyrule == 0)
            {
              YY_DPRINTF ((stderr, "Stack %ld dies.\n", YY_CAST (long, yyk)));
              yymarkStackDeleted (yystackp, yyk);
              return yyok;
            }
          yyflag = yyglrReduce (yystackp, yyk, yyrule, yyimmediate[yyrule]);
          if (yyflag == yyerr)
            {
              YY_DPRINTF ((stderr,
                           "Stack %ld dies "
                           "(predicate failure or explicit user error).\n",
                           YY_CAST (long, yyk)));
              yymarkStackDeleted (yystackp, yyk);
              return yyok;
            }
          if (yyflag != yyok)
            return yyflag;
        }
      else
        {
          yySymbol yytoken = yygetToken (&yychar);
          const short* yyconflicts;
          const int yyaction = yygetLRActions (yystate, yytoken, &yyconflicts);
          yystackp->yytops.yylookaheadNeeds[yyk] = yytrue;

          while (*yyconflicts != 0)
            {
              YYRESULTTAG yyflag;
              ptrdiff_t yynewStack = yysplitStack (yystackp, yyk);
              YY_DPRINTF ((stderr, "Splitting off stack %ld from %ld.\n",
                           YY_CAST (long, yynewStack), YY_CAST (long, yyk)));
              yyflag = yyglrReduce (yystackp, yynewStack,
                                    *yyconflicts,
                                    yyimmediate[*yyconflicts]);
              if (yyflag == yyok)
                YYCHK (yyprocessOneStack (yystackp, yynewStack,
                                          yyposn));
              else if (yyflag == yyerr)
                {
                  YY_DPRINTF ((stderr, "Stack %ld dies.\n", YY_CAST (long, yynewStack)));
                  yymarkStackDeleted (yystackp, yynewStack);
                }
              else
                return yyflag;
              yyconflicts += 1;
            }

          if (yyisShiftAction (yyaction))
            break;
          else if (yyisErrorAction (yyaction))
            {
              YY_DPRINTF ((stderr, "Stack %ld dies.\n", YY_CAST (long, yyk)));
              yymarkStackDeleted (yystackp, yyk);
              break;
            }
          else
            {
              YYRESULTTAG yyflag = yyglrReduce (yystackp, yyk, -yyaction,
                                                yyimmediate[-yyaction]);
              if (yyflag == yyerr)
                {
                  YY_DPRINTF ((stderr,
                               "Stack %ld dies "
                               "(predicate failure or explicit user error).\n",
                               YY_CAST (long, yyk)));
                  yymarkStackDeleted (yystackp, yyk);
                  break;
                }
              else if (yyflag != yyok)
                return yyflag;
            }
        }
    }
  return yyok;
}

static void
yyreportSyntaxError (yyGLRStack* yystackp)
{
  if (yystackp->yyerrState != 0)
    return;
#if ! YYERROR_VERBOSE
  yyerror (YY_("syntax error"));
#else
  {
  yySymbol yytoken = yychar == YYEMPTY ? YYEMPTY : YYTRANSLATE (yychar);
  yybool yysize_overflow = yyfalse;
  char* yymsg = YY_NULLPTR;
  enum { YYERROR_VERBOSE_ARGS_MAXIMUM = 5 };
  /* Internationalized format string. */
  const char *yyformat = YY_NULLPTR;
  /* Arguments of yyformat: reported tokens (one for the "unexpected",
     one per "expected"). */
  char const *yyarg[YYERROR_VERBOSE_ARGS_MAXIMUM];
  /* Actual size of YYARG. */
  int yycount = 0;
  /* Cumulated lengths of YYARG.  */
  ptrdiff_t yysize = 0;

  /* There are many possibilities here to consider:
     - If this state is a consistent state with a default action, then
       the only way this function was invoked is if the default action
       is an error action.  In that case, don't check for expected
       tokens because there are none.
     - The only way there can be no lookahead present (in yychar) is if
       this state is a consistent state with a default action.  Thus,
       detecting the absence of a lookahead is sufficient to determine
       that there is no unexpected or expected token to report.  In that
       case, just report a simple "syntax error".
     - Don't assume there isn't a lookahead just because this state is a
       consistent state with a default action.  There might have been a
       previous inconsistent state, consistent state with a non-default
       action, or user semantic action that manipulated yychar.
     - Of course, the expected token list depends on states to have
       correct lookahead information, and it depends on the parser not
       to perform extra reductions after fetching a lookahead from the
       scanner and before detecting a syntax error.  Thus, state merging
       (from LALR or IELR) and default reductions corrupt the expected
       token list.  However, the list is correct for canonical LR with
       one exception: it will still contain any token that will not be
       accepted due to an error action in a later state.
  */
  if (yytoken != YYEMPTY)
    {
      int yyn = yypact[yystackp->yytops.yystates[0]->yylrState];
      ptrdiff_t yysize0 = yytnamerr (YY_NULLPTR, yytokenName (yytoken));
      yysize = yysize0;
      yyarg[yycount++] = yytokenName (yytoken);
      if (!yypact_value_is_default (yyn))
        {
          /* Start YYX at -YYN if negative to avoid negative indexes in
             YYCHECK.  In other words, skip the first -YYN actions for this
             state because they are default actions.  */
          int yyxbegin = yyn < 0 ? -yyn : 0;
          /* Stay within bounds of both yycheck and yytname.  */
          int yychecklim = YYLAST - yyn + 1;
          int yyxend = yychecklim < YYNTOKENS ? yychecklim : YYNTOKENS;
          int yyx;
          for (yyx = yyxbegin; yyx < yyxend; ++yyx)
            if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR
                && !yytable_value_is_error (yytable[yyx + yyn]))
              {
                if (yycount == YYERROR_VERBOSE_ARGS_MAXIMUM)
                  {
                    yycount = 1;
                    yysize = yysize0;
                    break;
                  }
                yyarg[yycount++] = yytokenName (yyx);
                {
                  ptrdiff_t yysz = yytnamerr (YY_NULLPTR, yytokenName (yyx));
                  if (YYSIZEMAX - yysize < yysz)
                    yysize_overflow = yytrue;
                  else
                    yysize += yysz;
                }
              }
        }
    }

  switch (yycount)
    {
#define YYCASE_(N, S)                   \
      case N:                           \
        yyformat = S;                   \
      break
    default: /* Avoid compiler warnings. */
      YYCASE_(0, YY_("syntax error"));
      YYCASE_(1, YY_("syntax error, unexpected %s"));
      YYCASE_(2, YY_("syntax error, unexpected %s, expecting %s"));
      YYCASE_(3, YY_("syntax error, unexpected %s, expecting %s or %s"));
      YYCASE_(4, YY_("syntax error, unexpected %s, expecting %s or %s or %s"));
      YYCASE_(5, YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s"));
#undef YYCASE_
    }

  {
    /* Don't count the "%s"s in the final size, but reserve room for
       the terminator.  */
    ptrdiff_t yysz = YY_CAST (ptrdiff_t, strlen (yyformat)) - 2 * yycount + 1;
    if (YYSIZEMAX - yysize < yysz)
      yysize_overflow = yytrue;
    else
      yysize += yysz;
  }

  if (!yysize_overflow)
    yymsg = YY_CAST (char *, YYMALLOC (YY_CAST (size_t, yysize)));

  if (yymsg)
    {
      char *yyp = yymsg;
      int yyi = 0;
      while ((*yyp = *yyformat))
        {
          if (*yyp == '%' && yyformat[1] == 's' && yyi < yycount)
            {
              yyp += yytnamerr (yyp, yyarg[yyi++]);
              yyformat += 2;
            }
          else
            {
              ++yyp;
              ++yyformat;
            }
        }
      yyerror (yymsg);
      YYFREE (yymsg);
    }
  else
    {
      yyerror (YY_("syntax error"));
      yyMemoryExhausted (yystackp);
    }
  }
#endif /* YYERROR_VERBOSE */
  yynerrs += 1;
}

/* Recover from a syntax error on *YYSTACKP, assuming that *YYSTACKP->YYTOKENP,
   yylval, and yylloc are the syntactic category, semantic value, and location
   of the lookahead.  */
static void
yyrecoverSyntaxError (yyGLRStack* yystackp)
{
  if (yystackp->yyerrState == 3)
    /* We just shifted the error token and (perhaps) took some
       reductions.  Skip tokens until we can proceed.  */
    while (yytrue)
      {
        yySymbol yytoken;
        int yyj;
        if (yychar == YYEOF)
          yyFail (yystackp, YY_NULLPTR);
        if (yychar != YYEMPTY)
          {
            yytoken = YYTRANSLATE (yychar);
            yydestruct ("Error: discarding",
                        yytoken, &yylval);
            yychar = YYEMPTY;
          }
        yytoken = yygetToken (&yychar);
        yyj = yypact[yystackp->yytops.yystates[0]->yylrState];
        if (yypact_value_is_default (yyj))
          return;
        yyj += yytoken;
        if (yyj < 0 || YYLAST < yyj || yycheck[yyj] != yytoken)
          {
            if (yydefact[yystackp->yytops.yystates[0]->yylrState] != 0)
              return;
          }
        else if (! yytable_value_is_error (yytable[yyj]))
          return;
      }

  /* Reduce to one stack.  */
  {
    ptrdiff_t yyk;
    for (yyk = 0; yyk < yystackp->yytops.yysize; yyk += 1)
      if (yystackp->yytops.yystates[yyk] != YY_NULLPTR)
        break;
    if (yyk >= yystackp->yytops.yysize)
      yyFail (yystackp, YY_NULLPTR);
    for (yyk += 1; yyk < yystackp->yytops.yysize; yyk += 1)
      yymarkStackDeleted (yystackp, yyk);
    yyremoveDeletes (yystackp);
    yycompressStack (yystackp);
  }

  /* Now pop stack until we find a state that shifts the error token.  */
  yystackp->yyerrState = 3;
  while (yystackp->yytops.yystates[0] != YY_NULLPTR)
    {
      yyGLRState *yys = yystackp->yytops.yystates[0];
      int yyj = yypact[yys->yylrState];
      if (! yypact_value_is_default (yyj))
        {
          yyj += YYTERROR;
          if (0 <= yyj && yyj <= YYLAST && yycheck[yyj] == YYTERROR
              && yyisShiftAction (yytable[yyj]))
            {
              /* Shift the error token.  */
              int yyaction = yytable[yyj];
              YY_SYMBOL_PRINT ("Shifting", yystos[yyaction],
                               &yylval, &yyerrloc);
              yyglrShift (yystackp, 0, yyaction,
                          yys->yyposn, &yylval);
              yys = yystackp->yytops.yystates[0];
              break;
            }
        }
      if (yys->yypred != YY_NULLPTR)
        yydestroyGLRState ("Error: popping", yys);
      yystackp->yytops.yystates[0] = yys->yypred;
      yystackp->yynextFree -= 1;
      yystackp->yyspaceLeft += 1;
    }
  if (yystackp->yytops.yystates[0] == YY_NULLPTR)
    yyFail (yystackp, YY_NULLPTR);
}

#define YYCHK1(YYE)                                                          \
  do {                                                                       \
    switch (YYE) {                                                           \
    case yyok:                                                               \
      break;                                                                 \
    case yyabort:                                                            \
      goto yyabortlab;                                                       \
    case yyaccept:                                                           \
      goto yyacceptlab;                                                      \
    case yyerr:                                                              \
      goto yyuser_error;                                                     \
    default:                                                                 \
      goto yybuglab;                                                         \
    }                                                                        \
  } while (0)

/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
  int yyresult;
  yyGLRStack yystack;
  yyGLRStack* const yystackp = &yystack;
  ptrdiff_t yyposn;

  YY_DPRINTF ((stderr, "Starting parse\n"));

  yychar = YYEMPTY;
  yylval = yyval_default;

  if (! yyinitGLRStack (yystackp, YYINITDEPTH))
    goto yyexhaustedlab;
  switch (YYSETJMP (yystack.yyexception_buffer))
    {
    case 0: break;
    case 1: goto yyabortlab;
    case 2: goto yyexhaustedlab;
    default: goto yybuglab;
    }
  yyglrShift (&yystack, 0, 0, 0, &yylval);
  yyposn = 0;

  while (yytrue)
    {
      /* For efficiency, we have two loops, the first of which is
         specialized to deterministic operation (single stack, no
         potential ambiguity).  */
      /* Standard mode */
      while (yytrue)
        {
          yyStateNum yystate = yystack.yytops.yystates[0]->yylrState;
          YY_DPRINTF ((stderr, "Entering state %d\n", yystate));
          if (yystate == YYFINAL)
            goto yyacceptlab;
          if (yyisDefaultedState (yystate))
            {
              yyRuleNum yyrule = yydefaultAction (yystate);
              if (yyrule == 0)
                {
                  yyreportSyntaxError (&yystack);
                  goto yyuser_error;
                }
              YYCHK1 (yyglrReduce (&yystack, 0, yyrule, yytrue));
            }
          else
            {
              yySymbol yytoken = yygetToken (&yychar);
              const short* yyconflicts;
              int yyaction = yygetLRActions (yystate, yytoken, &yyconflicts);
              if (*yyconflicts != 0)
                break;
              if (yyisShiftAction (yyaction))
                {
                  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);
                  yychar = YYEMPTY;
                  yyposn += 1;
                  yyglrShift (&yystack, 0, yyaction, yyposn, &yylval);
                  if (0 < yystack.yyerrState)
                    yystack.yyerrState -= 1;
                }
              else if (yyisErrorAction (yyaction))
                {                  yyreportSyntaxError (&yystack);
                  goto yyuser_error;
                }
              else
                YYCHK1 (yyglrReduce (&yystack, 0, -yyaction, yytrue));
            }
        }

      while (yytrue)
        {
          yySymbol yytoken_to_shift;
          ptrdiff_t yys;

          for (yys = 0; yys < yystack.yytops.yysize; yys += 1)
            yystackp->yytops.yylookaheadNeeds[yys] = yychar != YYEMPTY;

          /* yyprocessOneStack returns one of three things:

              - An error flag.  If the caller is yyprocessOneStack, it
                immediately returns as well.  When the caller is finally
                yyparse, it jumps to an error label via YYCHK1.

              - yyok, but yyprocessOneStack has invoked yymarkStackDeleted
                (&yystack, yys), which sets the top state of yys to NULL.  Thus,
                yyparse's following invocation of yyremoveDeletes will remove
                the stack.

              - yyok, when ready to shift a token.

             Except in the first case, yyparse will invoke yyremoveDeletes and
             then shift the next token onto all remaining stacks.  This
             synchronization of the shift (that is, after all preceding
             reductions on all stacks) helps prevent double destructor calls
             on yylval in the event of memory exhaustion.  */

          for (yys = 0; yys < yystack.yytops.yysize; yys += 1)
            YYCHK1 (yyprocessOneStack (&yystack, yys, yyposn));
          yyremoveDeletes (&yystack);
          if (yystack.yytops.yysize == 0)
            {
              yyundeleteLastStack (&yystack);
              if (yystack.yytops.yysize == 0)
                yyFail (&yystack, YY_("syntax error"));
              YYCHK1 (yyresolveStack (&yystack));
              YY_DPRINTF ((stderr, "Returning to deterministic operation.\n"));
              yyreportSyntaxError (&yystack);
              goto yyuser_error;
            }

          /* If any yyglrShift call fails, it will fail after shifting.  Thus,
             a copy of yylval will already be on stack 0 in the event of a
             failure in the following loop.  Thus, yychar is set to YYEMPTY
             before the loop to make sure the user destructor for yylval isn't
             called twice.  */
          yytoken_to_shift = YYTRANSLATE (yychar);
          yychar = YYEMPTY;
          yyposn += 1;
          for (yys = 0; yys < yystack.yytops.yysize; yys += 1)
            {
              yyStateNum yystate = yystack.yytops.yystates[yys]->yylrState;
              const short* yyconflicts;
              int yyaction = yygetLRActions (yystate, yytoken_to_shift,
                              &yyconflicts);
              /* Note that yyconflicts were handled by yyprocessOneStack.  */
              YY_DPRINTF ((stderr, "On stack %ld, ", YY_CAST (long, yys)));
              YY_SYMBOL_PRINT ("shifting", yytoken_to_shift, &yylval, &yylloc);
              yyglrShift (&yystack, yys, yyaction, yyposn,
                          &yylval);
              YY_DPRINTF ((stderr, "Stack %ld now in state #%d\n",
                           YY_CAST (long, yys),
                           yystack.yytops.yystates[yys]->yylrState));
            }

          if (yystack.yytops.yysize == 1)
            {
              YYCHK1 (yyresolveStack (&yystack));
              YY_DPRINTF ((stderr, "Returning to deterministic operation.\n"));
              yycompressStack (&yystack);
              break;
            }
        }
      continue;
    yyuser_error:
      yyrecoverSyntaxError (&yystack);
      yyposn = yystack.yytops.yystates[0]->yyposn;
    }

 yyacceptlab:
  yyresult = 0;
  goto yyreturn;

 yybuglab:
  YY_ASSERT (yyfalse);
  goto yyabortlab;

 yyabortlab:
  yyresult = 1;
  goto yyreturn;

 yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  goto yyreturn;

 yyreturn:
  if (yychar != YYEMPTY)
    yydestruct ("Cleanup: discarding lookahead",
                YYTRANSLATE (yychar), &yylval);

  /* If the stack is well-formed, pop the stack until it is empty,
     destroying its entries as we go.  But free the stack regardless
     of whether it is well-formed.  */
  if (yystack.yyitems)
    {
      yyGLRState** yystates = yystack.yytops.yystates;
      if (yystates)
        {
          ptrdiff_t yysize = yystack.yytops.yysize;
          ptrdiff_t yyk;
          for (yyk = 0; yyk < yysize; yyk += 1)
            if (yystates[yyk])
              {
                while (yystates[yyk])
                  {
                    yyGLRState *yys = yystates[yyk];
                    if (yys->yypred != YY_NULLPTR)
                      yydestroyGLRState ("Cleanup: popping", yys);
                    yystates[yyk] = yys->yypred;
                    yystack.yynextFree -= 1;
                    yystack.yyspaceLeft += 1;
                  }
                break;
              }
        }
      yyfreeGLRStack (&yystack);
    }

  return yyresult;
}

/* DEBUGGING ONLY */
#if YYDEBUG
static void
yy_yypstack (yyGLRState* yys)
{
  if (yys->yypred)
    {
      yy_yypstack (yys->yypred);
      YY_FPRINTF ((stderr, " -> "));
    }
  YY_FPRINTF ((stderr, "%d@%ld", yys->yylrState, YY_CAST (long, yys->yyposn)));
}

static void
yypstates (yyGLRState* yyst)
{
  if (yyst == YY_NULLPTR)
    YY_FPRINTF ((stderr, "<null>"));
  else
    yy_yypstack (yyst);
  YY_FPRINTF ((stderr, "\n"));
}

static void
yypstack (yyGLRStack* yystackp, ptrdiff_t yyk)
{
  yypstates (yystackp->yytops.yystates[yyk]);
}

static void
yypdumpstack (yyGLRStack* yystackp)
{
#define YYINDEX(YYX)                                                    \
  YY_CAST (long,                                                        \
           ((YYX)                                                       \
            ? YY_REINTERPRET_CAST (yyGLRStackItem*, (YYX)) - yystackp->yyitems \
            : -1))

  yyGLRStackItem* yyp;
  for (yyp = yystackp->yyitems; yyp < yystackp->yynextFree; yyp += 1)
    {
      YY_FPRINTF ((stderr, "%3ld. ",
                   YY_CAST (long, yyp - yystackp->yyitems)));
      if (*YY_REINTERPRET_CAST (yybool *, yyp))
        {
          YY_ASSERT (yyp->yystate.yyisState);
          YY_ASSERT (yyp->yyoption.yyisState);
          YY_FPRINTF ((stderr, "Res: %d, LR State: %d, posn: %ld, pred: %ld",
                       yyp->yystate.yyresolved, yyp->yystate.yylrState,
                       YY_CAST (long, yyp->yystate.yyposn),
                       YYINDEX (yyp->yystate.yypred)));
          if (! yyp->yystate.yyresolved)
            YY_FPRINTF ((stderr, ", firstVal: %ld",
                         YYINDEX (yyp->yystate.yysemantics.yyfirstVal)));
        }
      else
        {
          YY_ASSERT (!yyp->yystate.yyisState);
          YY_ASSERT (!yyp->yyoption.yyisState);
          YY_FPRINTF ((stderr, "Option. rule: %d, state: %ld, next: %ld",
                       yyp->yyoption.yyrule - 1,
                       YYINDEX (yyp->yyoption.yystate),
                       YYINDEX (yyp->yyoption.yynext)));
        }
      YY_FPRINTF ((stderr, "\n"));
    }

  YY_FPRINTF ((stderr, "Tops:"));
  {
    ptrdiff_t yyi;
    for (yyi = 0; yyi < yystackp->yytops.yysize; yyi += 1)
      YY_FPRINTF ((stderr, "%ld: %ld; ", YY_CAST (long, yyi),
                   YYINDEX (yystackp->yytops.yystates[yyi])));
    YY_FPRINTF ((stderr, "\n"));
  }
#undef YYINDEX
}
#endif

#undef yylval
#undef yychar
#undef yynerrs



#line 2257 "../src/parser/fol.y"


/******************* function definitions ****************************/

  //warnDuplicates set to true by default
bool runYYParser(MLN* const & mln, Domain* const & dom,
                 const char* const & fileName, 
                 const bool& allPredsExceptQueriesAreClosedWorld,
                 const StringHashArray* const & openWorldPredNames,
                 const StringHashArray* const & closedWorldPredNames,
                 const StringHashArray* const & queryPredNames,
                 const bool& addUnitClauses, const bool& warnDuplicates,
                 const double& defaultWt, const bool& mustHaveWtOrFullStop,
                 const Domain* const & domain0, const bool& lazyInference,
                 const bool& flipWtsOfFlippedClause)
{
  zzinit();
  if (fileName) { yyin = fopen(fileName, "r" ); zzinFileName = fileName; }
  else            yyin = stdin;
  if (yyin == NULL) zzexit("Failed to open file %s.", fileName);

  signal(SIGFPE,zzsigHandler);
  signal(SIGABRT,zzsigHandler);
  signal(SIGILL,zzsigHandler);
  signal(SIGSEGV,zzsigHandler);

  zzwarnDuplicates = warnDuplicates;
  zzdefaultWt = defaultWt;
  zzmustHaveWtOrFullStop = mustHaveWtOrFullStop;
  zzflipWtsOfFlippedClause = flipWtsOfFlippedClause;

  ungetc('\n', yyin); // pretend that file begin with a newline
  zzmln = mln;
  zzdomain = dom;

  zzanyTypeId = zzdomain->getTypeId(PredicateTemplate::ANY_TYPE_NAME);
  zzassert(zzanyTypeId >= 0, "expecting zzanyTypeId >= 0");

  // Declare internally implemented predicates and functions
  //declareInternalPredicatesAndFunctions();

  zzisParsing = true;
  yyparse();
  zzisParsing = false;

  zzcheckAllTypesHaveConstants(zzdomain);
  zzcreateBlocks(zzdomain);
  
  // Insert groundings generated from internally implemented functions and predicates
  zzgenerateGroundingsFromInternalPredicatesAndFunctions();

  // Insert groundings generated from linked-in predicates
  if (zzusingLinkedPredicates) zzgenerateGroundingsFromLinkedPredicates(zzdomain);

  // Insert groundings generated from linked-in functions
  if (zzusingLinkedFunctions) zzgenerateGroundingsFromLinkedFunctions(zzdomain);

  if (zzok)
  {
      //append the formulas to MLN and set the weights of the hard clauses
    cout << "Adding clauses to MLN..." << endl;
    zzappendFormulasToMLN(zzformulaInfos, mln, domain0);

    if (addUnitClauses) zzappendUnitClausesToMLN(zzdomain, zzmln, zzdefaultWt);

    zzmln->setClauseInfoPriorMeansToClauseWts();

      // Change the constant ids so that constants of same type are ordered 
      // consecutively. Also ensure that the constants in the mln and map is 
      // consistent with the new constant ids
    zzdomain->reorderConstants(zzmln, zzpredIdToGndPredMap);

    zzmln->compress();

    Array<bool> isClosedWorldArr; 
    zzfillClosedWorldArray(isClosedWorldArr,allPredsExceptQueriesAreClosedWorld,
                           openWorldPredNames, closedWorldPredNames,
                           queryPredNames);

    Database* db = new Database(zzdomain, isClosedWorldArr, zzstoreGroundPreds);
    if (lazyInference) db->setLazyFlag();
    zzaddGndPredsToDb(db);
    zzdomain->setDB(db);
    zzdomain->compress();
  }
  
  if (zznumErrors > 0) cout << "Num of errors detected = " << zznumErrors<<endl;

  zzcleanUp();

  signal(SIGFPE,SIG_DFL);
  signal(SIGABRT,SIG_DFL);
  signal(SIGILL,SIG_DFL);
  signal(SIGSEGV,SIG_DFL);

  return zzok;
}

