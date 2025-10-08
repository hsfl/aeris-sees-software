#ifndef SEES_HPP
#define SEES_HPP

#include <Arduino.h>
#include "SEEs_Interface.hpp"

// ============================================================================
//  SEEs MODULE INTERFACE
//  ---------------------------------------------------------------------------
//  Declares top-level functions for initializing and running the SEEs
//  test/integration sequence. This is the public face of the driver logic
//  exposed to main.cpp.
// ============================================================================

namespace SEEs {
    void initialize();    // Called once during setup()
    void run_cycle();     // Called repeatedly during loop()
}

#endif