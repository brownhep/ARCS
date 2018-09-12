/*
 * NewPoint.h
 *
 *  Created on: Jul 26, 2009
 *      Author: lacasta
 */

#ifndef NEWPOINT_H_
#define NEWPOINT_H_
#include <GTimer.h>

/**
 * This is a class that controls if we need to change to a new
 * scan point.
 */
class NewPoint
{
    private:
        bool started;
    public:
        /// Constructor
        NewPoint() : started(false)
        {}
        virtual ~NewPoint()
        {}
        // Returns true if we need to start a new point
        virtual bool operator()(int ievt) =0;

        // Resets the state
        virtual void reset()
        {}

        // "increments" the state
        virtual void next(int ievt)
        {}

        virtual bool has_started() const
        {
            return started;
        }
        virtual void start()
        {
            started = true;
        }
        virtual double value() const { return 0.0; }
        virtual void value(double x) {}
};

/**
 * Changes from one point to the next based on a fixed number
 * of events per point in the scan
 */
class EventCntr : public NewPoint
{
    private:
        /// Total number of event
        int nevts;

        /// Current event
        int ievt;
    public:
        /// Constructor
        EventCntr(int n) : nevts(n), ievt(0)
        {}

        /// Destructor
        virtual ~EventCntr()
        {}

        /// returns true if we need to change to a new point
        bool operator()(int evt)
        {
            if ( evt-ievt >= nevts)
            {
                ievt = evt;
                return true;
            }
            else
                return false;
        }

        /// resets the current event
        void reset()
        {
            ievt = 0;
        }
        void next()
        {
            ievt++;
        }
        double value() const { return nevts; }
        void value(double x) { nevts = int(x); }
};

/**
 *  Changes from one point in the scan to the next based on
 * a fixed ammount of time spent on each point
 */
class EventTimer : public NewPoint
{
    private:
        /// Maximum time for a scan point
        double mxtime;

        /// A timer
        AlibavaTimer timer;
    public:
        /// Constructor
        EventTimer(double mx) : mxtime(mx)
        {
            timer.reset();
            timer.stop();
        }

        /// Destructor
        ~EventTimer()
        {}

        /// returns true if we need to change to a new point
        bool operator()(int ievt)
        {
            if (!has_started())
            {
                start();
                return true;
            }
            else
            {
                double t = timer();
                return t> mxtime;
            }
        }
        double value() const { return mxtime; }
        void value(double x) { mxtime=x; }

        void reset()
        {
            timer.reset();
            timer.start();
        }
};



#endif /* NEWPOINT_H_ */
