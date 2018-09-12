/*
 * Plugin.h
 *
 * This is an abstract class that defines the interface for a plugin.
 * It defines a number of methods that called at various stages of the
 * DAQ process
 *
 *
 *  Created on: Jul 23, 2009
 *      Author: lacasta
 */

#ifndef PLUGIN_H_
#define PLUGIN_H_

#include <DataFormat.h>

class Plugin
{
    private:
        bool _active;
    public:
        Plugin() : _active(false) {}
        virtual ~Plugin() {}

        enum BlockType { NewFile=0, StartOfRun, DataBlock, CheckPoint, EndOfRun };
        enum RunType
        {
            Unknown=0,
            Calibration=1,
            LaserSync,
            Laser,
            RadSource,
            Pedestal,
            LastRType
        };

        bool active() const { return _active; }
        void active(bool val) { _active = val; }

        /**
         * Called at the beginning of a new file. It will return a
         * buffer with user specific information that will be stored
         * in the file header.
         *
         */
        virtual void new_file(std::string &buffer)
        {
            return;
        }

        /**
         * Called at the beginning of a run. Returns the number
         * of "real" events that the user wants.
         *
         * This may sound bizarre, but it is a way to define, together
         * with the new_event user specific scans where the total number
         * of events is number of points times number of events per point.
         */
        virtual int start_of_run(int run_type, int nevts, int sample_size)
        {
            return nevts;
        }

        /**
         * This is called at the end of a run. It can return a buffer with some
         * user data that can be, later on during the analysis phase, retrieved.
         */
        virtual void end_of_run(std::string &S)
        {
            return;
        }

        /**
         * Called at the beginning of each new event. If it returns true, the
         * method new_point will be called right afterwards.
         *
         * If the user wants to implement its own scan, he/she is responsible
         * for deciding when to change to the next point. The return value is
         * true when a new point record has to be written in the file and false
         * otherwise. The method new_point will return the buffer to be stored
         * on the new point record.
         *
         * The argument is the current event number
         */
        virtual bool new_event(int evt)
        {
            return false;
        }

        /**
         * Returns a buffer to be stored in a new_point record. This method
         * is usually called after new_event returning true
         */
        virtual void new_point(std::string &S)
        {
            return;
        }

        /**
         * Filters an event and produces user-defined output data in the
         * EventData block, instead of the usual EventData dump
         */
        virtual int filter_event(const EventData *, std::string &S)
        {
            return 0;
        }

        virtual bool good() const { return true; }
};

typedef Plugin * (*PluginBuilder)();

#endif /* PLUGIN_H_ */
