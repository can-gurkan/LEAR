# LEAR
LLM-driven Evolution of Agent Rules

## Overview

This project explores the use of **Large Language Models (LLMs)** within **Agent-Based Modeling (ABM)** environments to iteratively enhance agent movement and functionality through **automated code generation**.

Traditional genetic programming typically relies on **mutation operators** — small, stochastic changes applied to numerical agent behaviors — to explore behavior spaces (Poli et al., 2013). This project introduces and evaluates a **novel approach** by leveraging **LLM-driven code generation** as an advanced mutation operator.

## Approach

- **Traditional Method**: Utilizes conventional mutation operators to introduce slight, random variations in agent behavior.
- **Proposed Method**: Integrates LLMs to autonomously generate, modify, and optimize the agent behavior code based on iterative feedback from the environment.

## Goal

The primary objective is to **compare the effectiveness** of LLM-generated mutations against traditional mutation strategies used in genetic programming. By doing so, the project seeks to assess whether LLMs can provide a more sophisticated and efficient mechanism for evolving agent behaviors.

## Installation

### Prerequisites

- [Rye](https://rye-up.com/) (for Python dependency and environment management)
- [NetLogo](https://ccl.northwestern.edu/netlogo/) (for Agent-Based Modeling)

> **Note:** Ensure you have Python installed (Rye will manage Python versions internally if needed).

### Step 1: Install Rye

Follow the official instructions to install Rye:

```bash
curl -sSf https://rye-up.com/get | bash
```

#### Optional Step: Add Shims to Path
Follow [these](https://rye.astral.sh/guide/installation/#add-shims-to-path) instructions to add "shims" to your folder, which are executables that Rye manages for you as well as the rye executable itself.

#### After installation,
restart your terminal or run:

```bash
source ~/.rye/env
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/can-gurkan/LEAR.git
cd your-repository-name
```

### Step 3: Set Up the Python Environment

Initialize Rye and sync dependencies:

```bash
rye sync
```

This will automatically create a virtual environment and install all required Python packages.

### Step 4: Install NetLogo

Download and install NetLogo from the [official site](https://ccl.northwestern.edu/netlogo/).

Make sure NetLogo is accessible from your system path or note the installation directory for later configuration.

### Step 5: Configure Environment Variables (if needed)

If your project requires pointing to the NetLogo installation path, you can set an environment variable:

```bash
export NETLOGO_HOME=/path/to/netlogo
```

Alternatively, update your configuration file or code as needed to locate NetLogo.

---



## Citation
Poli, Riccardo, et al. "Genetic programming: An introductory tutorial and a survey of techniques 
    and applications." Univ. Essex School of Computer Science and Electronic Engineering 
    Technical Report No. CES-475 (2007): 1-112.

