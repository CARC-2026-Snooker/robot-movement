#pragma once

#include "PRIZM.h"

// Data types
enum TransitionType {
    QUADRATIC,
    CUBIC,
    QUARTIC,
    SQUARE_ROOT,
    CUBE_ROOT,
    FOURTH_ROOT,
    POLYNOMIAL
};
enum Direction {
    NONE, // May use for stop
    FRONT,
    // FRONT_LEFT,
    LEFT,
    // BACK_LEFT,
    BACK,
    // BACK_RIGHT,
    RIGHT
    // FRONT_RIGHT
};

// C++ type replacements
struct irActivation {
    bool flActivation;
    bool frActivation;
    bool rlActivation;
    bool rrActivation;
};
struct wheelDirections {
    int flDirection;
    int frDirection;
    int rlDirection;
    int rrDirection;
};

// Component
struct irArray {
    // Hold the pin correspond to each ir
    int fl = 7; // Front left
    int fr = 6; // Front right
    int rl = 5; // Rear left
    int rr = 4; // Rear right
};
struct Wheel {
    int id;
    int channel;
};
struct Wheels {
    Wheel fl = {1, 1}; // Front left
    Wheel fr = {2, 1}; // Front right
    Wheel rl = {1, 2}; // Rear left
    Wheel rr = {2, 2}; // Rear right
};

class BaseRobot {
    private:
        PRIZM prizm;
        EXPANSION exc;

        // IR Sensor
        irArray irArrayPins;
        bool isIrActivateHigh;

        // Wheels (ID, Channel)
        Wheels wheels;
        Wheel wheelFl; // Front left
        Wheel wheelFr; // Front right
        Wheel wheelRl; // Rear left
        Wheel wheelRr; // Rear right
        float wheelCircumference; // For calculating distance

        // Base constructor function
        void baseConstructor();

        // IR function
        irActivation readIr();
        Direction mapIrToDirection();

        // Movement function
        float mapTransition(float input, TransitionType transitionType);
        int projectTransitionToSpeed(Wheel wheel, unsigned int speed, int target, TransitionType transitionType);

        wheelDirections mapWheelDirection(Direction direction);
        void move(unsigned int speed, Direction direction);
        void moveUntilBlack(unsigned int speed, Direction direction);

        void calibrateMove();
    public:
        BaseRobot();
        BaseRobot(bool irActivateHigh, irArray irArrayPins, Wheels wheels);
        void transitionMove(unsigned int speed, int target, TransitionType transitionType, float error = 0.1);
};
