__MAX = 255
__MID = __MAX // 2
__MIN = 0
        
RED            = (__MAX, __MIN, __MIN)
ORANGE         = (__MAX, __MID, __MIN)
YELLOW         = (__MAX, __MAX, __MIN)
LIME           = (__MID, __MAX, __MIN)
GREEN          = (__MIN, __MAX, __MIN)
CYAN           = (__MIN, __MAX, __MAX)
SKY            = (__MIN, __MID, __MAX)
BLUE           = (__MIN, __MIN, __MAX)
MAGENTA        = (__MAX, __MIN, __MAX)
        
DARK_RED       = (__MID, __MIN, __MIN)
DARK_GREEN     = (__MIN, __MID, __MIN)
DARK_BLUE      = (__MIN, __MIN, __MID)
        
LIGHT_RED      = (__MAX, __MID, __MID)
LIGHT_GREEN    = (__MID, __MAX, __MID)
LIGHT_BLUE     = (__MID, __MID, __MAX)

CYAN           = (__MIN, __MAX, __MAX)
YELLOW         = (__MAX, __MAX, __MIN)
MAGENTA        = (__MAX, __MIN, __MAX)

DARK_CYAN      = (__MIN, __MID, __MID)
DARK_YELLOW    = (__MID, __MID, __MIN)
DARK_MAGENTA   = (__MID, __MIN, __MID)

LIGHT_CYAN     = (__MID, __MAX, __MAX)
LIGHT_YELLOW   = (__MAX, __MAX, __MID)
LIGHT_MAGENTA  = (__MAX, __MID, __MAX)
        
BLACK          = (__MIN, __MIN, __MIN)
WHITE          = (__MAX, __MAX, __MAX)
GRAY           = lambda x: (__MAX * x, __MAX * x, __MAX * x)