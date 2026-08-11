/**
 * Declared MOCK-until-onboarded sample data.
 *
 * Shown ONLY while the InvokeAI health probe reports not-configured.
 * Every surface carries a visible MOCK badge. Clears automatically when
 * /api/health reports configured=true. See docs/ONBOARDING.md "Declared doubles".
 */

export const MOCK = {
  dashboard: {
    modelCount: 3,
    queue: { queued: 2, in_progress: 1, completed: 47, failed: 0, canceled: 1 },
    version: "5.7.0",
    recentImages: [
      {
        image_name: "mock-joe-mocky-1.png",
        url: "",
        thumbnail_url: "",
      },
      {
        image_name: "mock-sandra-mockinger-2.png",
        url: "",
        thumbnail_url: "",
      },
    ],
  },
  models: [
    { name: "Joe Mocky SDXL", key: "mock-sdxl", base: "sdxl", type: "main" },
    {
      name: "Sandra Mockinger Flux",
      key: "mock-flux",
      base: "flux",
      type: "main",
    },
    {
      name: "Realistic Mock V1.5",
      key: "mock-sd15",
      base: "sd-1",
      type: "main",
    },
  ],
  gallery: [
    {
      image_name: "mock-preview-1.png",
      prompt: "[MOCK] neon city sample",
      url: "",
      thumbnail_url: "",
    },
    {
      image_name: "mock-preview-2.png",
      prompt: "[MOCK] lighthouse sample",
      url: "",
      thumbnail_url: "",
    },
  ],
};

export const MOCK_BANNER =
  "Sample data - connect InvokeAI to see live content (complete onboarding).";
