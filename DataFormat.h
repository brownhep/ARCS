/* -*- mode: c++ -*- */
#ifndef __DataFormat_h__
#define __DataFormat_h__

#include <memory>
#include <USBport.h>
#include <DataReceiver.h>

/**
 *  Data is received from the USB port with this format:
 *  Firmware V0: time(i), temp(s), data[256](s)
 *  Firmware V1: time(i), temp(s), [header[16](s),data[128](s)] x number_of_chips
 *
 *  In calibration mode neither the time nor the temperature are passed
 *
 */

/*
 * The data coming from a chip
 */
struct Chip
{
        unsigned short header[16];
        unsigned short signal[128];
};
/*
 * This is the basic data chunk coming from USB
 */
struct EventBlock
{
        unsigned int time;
        unsigned short temp;
        Chip chip[2];
};


#define BlockSize 518


/**
 * The data is passed in the application.
 *
 * We add value as an extra parameter when moving the
 * data within the application. It tells the value of
 * the variables which are scanned
 */
class EventData
{
    private:
        // Value associated with scanned variables
        double _value;

        // Number of chips
        int _nchip;

        // firmware version
        int _firmware;

        // chip mask
        int _mask;

        /// The data allocator
        static std::allocator<char> data_allocator;

    protected:
        // Pointer to the USB data
        int psize;
        EventBlock block;

//        union {
//            char   *ptr;
//            EventBlock *block;
//        } d;

        EventData();
        void set_nchip(int nc);

    public:
        virtual ~EventData();

        // nchip <0 old USB data format
        static EventData *factory(int nchip, int firmware, int mask);

        double value() const { return _value; }
        void   value(double x) { _value = x; }

        int firmware() const { return _firmware; }
        int mask() const { return _mask; }
        int nchip() const { return _nchip; }

        const EventBlock *get_block() const { return &block; }
        EventBlock *get_block() { return &block; }

        unsigned int time() const { return block.time; }
        unsigned short temp() const { return block.temp; }

        const Chip *chip(int i=0) const { return &block.chip[i]; }
        Chip *chip(int i=0) { return &block.chip[i]; }

        /*
         * This is to read from USB
         */
        virtual int read_data(USBport &port)=0;
        virtual int size_calib() = 0;
        virtual int size_data() = 0;
};


#endif
