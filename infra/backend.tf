terraform {
  backend "gcs" {
    bucket  = "mindmirror-tofu-state"
    prefix  = "envs/default"
  }
}
