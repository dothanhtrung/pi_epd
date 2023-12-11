use embedded_graphics::prelude::*;
use epd_waveshare::color::Color;
use epd_waveshare::epd3in7::{Display3in7, EPD3in7};
use epd_waveshare::prelude::WaveshareDisplay;
use linux_embedded_hal::{Delay, SpidevDevice, SysfsPin};
use linux_embedded_hal::spidev::{Spidev, SpidevOptions};
use linux_embedded_hal::spidev;
use linux_embedded_hal::sysfs_gpio::Direction;

fn main() {
    let busy = SysfsPin::new(24);
    busy.export().expect("cannot export busy");
    while !busy.is_exported() {};
    busy.set_direction(Direction::In).expect("Cannot set direction");

    let dc = SysfsPin::new(25);
    dc.export().expect("Failed dc export");
    while !dc.is_exported() {}
    dc.set_direction(Direction::Out).expect("failed to set direction for dc");

    let rst = SysfsPin::new(17);
    rst.export().expect("failed to export rst");
    while !rst.is_exported() {}
    rst.set_direction(Direction::Out).expect("Failed to set rst direction");

    let cs = SysfsPin::new(26);
    cs.export().expect("failed to export cs");
    while !cs.is_exported() {}
    cs.set_direction(Direction::Out).expect("failed to set cs direction");
    cs.set_value(1).expect("cs value set to 1");

    let mut spi = SpidevDevice::open("/dev/spidev0.0").expect("spidev directory");
    let options = SpidevOptions::new().bits_per_word(8).max_speed_hz(10_000_000).mode(spidev::SpiModeFlags::SPI_MODE_0).build();
    spi.configure(&options).expect("spi configuration");

    let mut delay = Delay {};

    let mut epd = EPD3in7::new(&mut spi, busy, dc, rst, &mut delay, None).expect("eink init error");

    let mut display = Display3in7::default();
    display.clear(Color::White).ok();

    epd.update_and_display_frame(&mut spi, display.buffer(), &mut delay).expect("Failed to update and display frame");
}
