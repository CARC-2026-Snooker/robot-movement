#include "BaseRobot.h"

#include <math.h>

// Constructor
void BaseRobot::baseConstructor() {
    prizm.PrizmBegin();

    pinMode(irArrayPins.fl, INPUT);
    pinMode(irArrayPins.fr, INPUT);
    pinMode(irArrayPins.rl, INPUT);
    pinMode(irArrayPins.rr, INPUT);

    calibrateMove();
}
BaseRobot::BaseRobot()
    : isIrActivateHigh(true) {
    baseConstructor();
}
BaseRobot::BaseRobot(bool irActivateHigh, irArray irArrayPins, Wheels wheels)
    : isIrActivateHigh(irActivateHigh), irArrayPins(irArrayPins), wheels(wheels) {
    baseConstructor();
}

// IR helper function
irActivation BaseRobot::readIr() {
    // Return whether each IR is activated. If it is activated the value will be true.
    // Fl, Fr, Rl, Rr is the position of each ir in the tuple.
    irActivation out = {
        digitalRead(irArrayPins.fl) == isIrActivateHigh,
        digitalRead(irArrayPins.fr) == isIrActivateHigh,
        digitalRead(irArrayPins.rl) == isIrActivateHigh,
        digitalRead(irArrayPins.rr) == isIrActivateHigh
    };
    return out;
}
Direction BaseRobot::mapIrToDirection() {
    // Map the IR value combination to the direction of the black line.
    // If there imbalance in IR activation (เอียง), Direction::NONE will be return.
    irActivation irRead = readIr();
    int leftActivationWeight = irRead.flActivation + irRead.rlActivation;
    int rightActivationWeight = irRead.frActivation + irRead.rrActivation;

    if (leftActivationWeight == rightActivationWeight && leftActivationWeight != 0) {
        return Direction::FRONT;
    } else if (leftActivationWeight == 2 && rightActivationWeight == 0) {
        return Direction::LEFT;
    } else if (leftActivationWeight == 0 && rightActivationWeight == 2) {
        return Direction::RIGHT;
    }
    return Direction::NONE;
}

// Movement helper function
float BaseRobot::mapTransition(float input, TransitionType transitionType) {
    // Input between 0 to 1

    switch (transitionType) {
        case TransitionType::QUADRATIC:
            return 1 - pow(input, 2);
        case TransitionType::CUBIC:
            return 1 - pow(input, 3);
        case TransitionType::QUARTIC:
            return 1 - pow(input, 4);

        case TransitionType::SQUARE_ROOT:
            return 1 - pow(input, 1/2);
        case TransitionType::CUBE_ROOT:
            return 1 - pow(input, 1/3);
        case TransitionType::FOURTH_ROOT:
            return 1 - pow(input, 1/4);

        case TransitionType::POLYNOMIAL:
            return 1 - 3 * pow(input, 2) + 2 * pow(input, 3);

        default:
            return 1.0f;
    }
}
int BaseRobot::projectTransitionToSpeed(Wheel wheel, unsigned int speed, int target, TransitionType transitionType) {
    // Project the max speed to the transition graph reference to the encoder reading to target.
    int currentReading = exc.readServoPosition(wheel.id, wheel.channel);
    float transitionPosition = mapTransition(currentReading / target, transitionType);
    return floor(transitionPosition * speed);
}

wheelDirections BaseRobot::mapWheelDirection(Direction direction) {
    // Map directory down into multiplier of each motor.
    // Fl, Fr, Rl, Rr
    switch (direction) {
        case Direction::FRONT:
            return wheelDirections({-1, -1, 1, 1});
        case Direction::LEFT:
            return wheelDirections({1, -1, 1, -1});
        case Direction::BACK:
            return wheelDirections({1, 1, -1, -1});
        case Direction::RIGHT:
            return wheelDirections({-1, 1, -1, 1});
    }
}
void BaseRobot::move(unsigned int speed, Direction direction) {
    wheelDirections wheelDirection = mapWheelDirection(direction);
    exc.setMotorSpeed(wheelFl.id, wheelFl.channel, speed * wheelDirection.flDirection);
    exc.setMotorSpeed(wheelFr.id, wheelFr.channel, speed * wheelDirection.frDirection);
    exc.setMotorSpeed(wheelRl.id, wheelRl.channel, speed * wheelDirection.rlDirection);
    exc.setMotorSpeed(wheelRr.id, wheelRr.channel, speed * wheelDirection.rrDirection);
}
void BaseRobot::moveUntilBlack(unsigned int speed, Direction direction) {
    move(speed, direction);
    while (mapIrToDirection() != direction);
    move(0, direction);
}
void BaseRobot::calibrateMove() {
    moveUntilBlack(50, Direction::FRONT);
    moveUntilBlack(50, Direction::LEFT);
}

// Public function
void BaseRobot::transitionMove(unsigned int speed, int target, TransitionType transitionType, float error) {
    // Continuously calling projectSpeedToTransition, blocking all code execution.
    // while (exc.readServoPosition() > target * (1 + error) || exc.readServoPosition() < target * (1 - error)) {
    //     int targetSpeed = projectTransitionToSpeed();

    // }
}