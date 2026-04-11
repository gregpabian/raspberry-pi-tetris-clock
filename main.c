/*
 * Tetris Clock - Main entry point.
 *
 * Displays time using falling Tetris blocks on a 64x32 RGB LED matrix.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <time.h>
#include <getopt.h>

#include "tetris_clock.h"
#include "tetris_render.h"

static volatile sig_atomic_t running = 1;

static void signal_handler(int sig)
{
    (void)sig;
    running = 0;
}

static void usage(const char *prog)
{
    fprintf(stderr,
        "Usage: %s [options]\n"
        "  --fps N                Target FPS (default: 20)\n"
        "  --ticks N              Animation ticks per frame (default: 2)\n"
        "  --brightness N         LED brightness 1-100 (default: 50)\n"
        "  --slowdown N           GPIO slowdown factor (default: 2)\n"
        "  --pwm-bits N           PWM bits 1-11 (default: 9)\n"
        "  --pwm-lsb-nanoseconds N  PWM LSB timing in ns (default: 300)\n"
        "  --pixel-scale N        Clock pixel scale factor (default: 2)\n"
#ifdef TEST_MODE
        "  --test-output DIR      Output directory (default: test_output)\n"
        "  --frames N             Max frames (default: 200)\n"
        "  --scale N              PNG scale factor (default: 8)\n"
#endif
        "  --help                 Show this help\n",
        prog);
}

int main(int argc, char *argv[])
{
    /* Defaults */
    int fps = 20;
    int ticks_per_frame = 2;
    int brightness = 50;
    int slowdown = 2;
    int pwm_bits = 9;
    int pwm_lsb_nanoseconds = 300;
    int pixel_scale = 2;
#ifdef TEST_MODE
    const char *test_output = "test_output";
    int max_frames = 200;
    int png_scale = 8;
#endif

    static struct option long_options[] = {
        {"fps",                  required_argument, 0, 'f'},
        {"ticks",                required_argument, 0, 't'},
        {"brightness",           required_argument, 0, 'b'},
        {"slowdown",             required_argument, 0, 's'},
        {"pwm-bits",             required_argument, 0, 'p'},
        {"pwm-lsb-nanoseconds", required_argument, 0, 'n'},
        {"pixel-scale",          required_argument, 0, 'x'},
#ifdef TEST_MODE
        {"test-output",          required_argument, 0, 'o'},
        {"frames",               required_argument, 0, 'F'},
        {"scale",                required_argument, 0, 'S'},
#endif
        {"help",                 no_argument,       0, 'h'},
        {0, 0, 0, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "", long_options, NULL)) != -1) {
        switch (opt) {
        case 'f': fps = atoi(optarg); break;
        case 't': ticks_per_frame = atoi(optarg); break;
        case 'b': brightness = atoi(optarg); break;
        case 's': slowdown = atoi(optarg); break;
        case 'p': pwm_bits = atoi(optarg); break;
        case 'n': pwm_lsb_nanoseconds = atoi(optarg); break;
        case 'x': pixel_scale = atoi(optarg); break;
#ifdef TEST_MODE
        case 'o': test_output = optarg; break;
        case 'F': max_frames = atoi(optarg); break;
        case 'S': png_scale = atoi(optarg); break;
#endif
        case 'h':
        default:
            usage(argv[0]);
            return (opt == 'h') ? 0 : 1;
        }
    }

    /* Signal handling */
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    /* Initialize clock */
    ClockState clock;
    clock_init(&clock, pixel_scale, DISPLAY_WIDTH, DISPLAY_HEIGHT);

    /* Initialize renderer */
    Renderer renderer;

#ifdef TEST_MODE
    /* Suppress unused warnings in test mode */
    (void)brightness;
    (void)slowdown;
    (void)pwm_bits;
    (void)pwm_lsb_nanoseconds;

    /* Create output directory */
    char mkdir_cmd[512];
    snprintf(mkdir_cmd, sizeof(mkdir_cmd), "mkdir -p %s", test_output);
    system(mkdir_cmd);

    renderer_init_test(&renderer, test_output, png_scale);
#else
    struct RGBLedMatrixOptions opts;
    struct RGBLedRuntimeOptions rt_opts;
    memset(&opts, 0, sizeof(opts));
    memset(&rt_opts, 0, sizeof(rt_opts));

    opts.rows = 32;
    opts.cols = 64;
    opts.hardware_mapping = "adafruit-hat";
    opts.led_rgb_sequence = "RGB";
    opts.brightness = brightness;
    opts.pwm_bits = pwm_bits;
    opts.pwm_lsb_nanoseconds = pwm_lsb_nanoseconds;
    rt_opts.gpio_slowdown = slowdown;
    rt_opts.drop_privileges = 0;

    struct RGBLedMatrix *matrix =
        led_matrix_create_from_options_and_rt_options(&opts, &rt_opts);
    if (!matrix) {
        fprintf(stderr, "Failed to create LED matrix\n");
        return 1;
    }
    renderer_init_matrix(&renderer, matrix);
#endif

    printf("Tetris Clock running (fps=%d, ticks=%d, pixel_scale=%d)\n",
           fps, ticks_per_frame, pixel_scale);

    /* Main loop */
    long frame_duration_ns = 1000000000L / fps;
    time_t last_time_check = 0;
    int frame_count = 0;

    while (running) {
        struct timespec frame_start, frame_end;
        clock_gettime(CLOCK_MONOTONIC, &frame_start);

        /* Check time once per second */
        time_t now_t = time(NULL);
        if (now_t != last_time_check) {
            struct tm *tm = localtime(&now_t);
            clock_update_time(&clock, tm->tm_hour, tm->tm_min, tm->tm_sec);
            last_time_check = now_t;
        }

        /* Advance animations */
        for (int t = 0; t < ticks_per_frame; t++)
            clock_tick(&clock);

        /* Render */
        RenderBlock blocks[MAX_RENDER_BLOCKS];
        int block_count = clock_get_render_blocks(&clock, blocks);
        int colon_count;
        const Pixel *colon = clock_get_colon_pixels(&clock, &colon_count);
        renderer_render_frame(&renderer, blocks, block_count,
                              colon, colon_count, pixel_scale);

        frame_count++;
#ifdef TEST_MODE
        if (max_frames > 0 && frame_count >= max_frames)
            break;
#endif

        /* Frame rate cap */
        clock_gettime(CLOCK_MONOTONIC, &frame_end);
        long elapsed_ns = (frame_end.tv_sec - frame_start.tv_sec) * 1000000000L
                        + (frame_end.tv_nsec - frame_start.tv_nsec);
        long sleep_ns = frame_duration_ns - elapsed_ns;
        if (sleep_ns > 0) {
            struct timespec ts = {0, sleep_ns};
            nanosleep(&ts, NULL);
        }
    }

    renderer_cleanup(&renderer);
    printf("\nStopped after %d frames.\n", frame_count);

#ifndef TEST_MODE
    led_matrix_delete(matrix);
#endif

    return 0;
}
